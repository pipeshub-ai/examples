// Upload your own files to a PipesHub knowledge base and wait until they are searchable.
//
// Usage:
//
//	export PIPESHUB_URL=http://localhost:3000
//	export PIPESHUB_BEARER_AUTH=<personal access token>
//	go run . "Team handbook" handbook.md onboarding.pdf
package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"os"
	"path/filepath"
	"strings"
	"time"

	pipeshub "github.com/pipeshub-ai/pipeshub-sdk-go"
	"github.com/pipeshub-ai/pipeshub-sdk-go/models/components"
	"github.com/pipeshub-ai/pipeshub-sdk-go/models/operations"
)

const indexTimeout = 10 * time.Minute

func main() {
	if len(os.Args) < 3 {
		log.Fatal(`usage: go run . "<knowledge base name>" <file> [file...]`)
	}
	kbName, paths := os.Args[1], os.Args[2:]
	baseURL := strings.TrimRight(os.Getenv("PIPESHUB_URL"), "/")
	if baseURL == "" {
		baseURL = "http://localhost:3000"
	}
	token := os.Getenv("PIPESHUB_BEARER_AUTH")
	if token == "" {
		log.Fatal("Set PIPESHUB_BEARER_AUTH to a Personal Access Token (Workspace -> Developer settings).")
	}
	client := pipeshub.New(
		pipeshub.WithServerURL(baseURL+"/api/v1"),
		pipeshub.WithSecurity(components.Security{BearerAuth: pipeshub.Pointer(token)}),
	)
	ctx := context.Background()

	kbID := findOrCreateKB(ctx, client, kbName)
	names := upload(ctx, client, kbID, paths)
	waitUntilIndexed(ctx, client, kbID, names)
	fmt.Printf("\nDone. Ask about them with the SDK starter, or in the PipesHub chat.\n")
}

// findOrCreateKB returns the id of the knowledge base called name, creating it if needed.
func findOrCreateKB(ctx context.Context, client *pipeshub.Pipeshub, name string) string {
	list, err := client.KnowledgeBase.ListKnowledgeBases(ctx, operations.ListKnowledgeBasesRequest{Search: &name})
	if err != nil {
		log.Fatalf("list knowledge bases: %v", err)
	}
	if list.GetAllKnowledgeBaseResponseSchema != nil {
		for _, kb := range list.GetAllKnowledgeBaseResponseSchema.KnowledgeBases {
			if kb.Name == name {
				fmt.Printf("Using knowledge base %q\n", name)
				return kb.ID
			}
		}
	}
	created, err := client.KnowledgeBase.CreateKnowledgeBase(ctx, operations.CreateKnowledgeBaseRequest{KbName: name})
	if err != nil {
		log.Fatalf("create knowledge base: %v", err)
	}
	fmt.Printf("Created knowledge base %q\n", name)
	return created.KnowledgeBaseCreateResponse.ID
}

// upload sends the files in one request and reports each file's result as the server streams it.
func upload(ctx context.Context, client *pipeshub.Pipeshub, kbID string, paths []string) []string {
	var files []operations.UploadRecordsFile
	var names []string
	for _, p := range paths {
		data, err := os.ReadFile(p)
		if err != nil {
			log.Fatalf("read %s: %v", p, err)
		}
		name := filepath.Base(p)
		files = append(files, operations.UploadRecordsFile{FileName: name, Content: data})
		names = append(names, name)
	}
	fmt.Printf("Uploading %d file(s)...\n", len(files))
	res, err := client.KnowledgeBase.UploadRecords(ctx, kbID, operations.UploadRecordsRequestBody{Files: files}, nil)
	if err != nil {
		log.Fatalf("upload: %v", err)
	}
	stream := res.UploadStreamSSEEvent
	defer stream.Close()
	failed := 0
	for stream.Next() {
		ev := stream.Value()
		if ev == nil || ev.Event == nil {
			continue
		}
		data := ""
		if ev.Data != nil {
			data = *ev.Data
		}
		// Each file event carries the file's name and, on failure, why.
		var file struct {
			FileName string   `json:"fileName"`
			Errors   []string `json:"errors"`
			Reason   string   `json:"reason"`
		}
		_ = json.Unmarshal([]byte(data), &file)
		switch *ev.Event {
		case components.UploadStreamSSEEventEventFileSucceeded:
			fmt.Println("  uploaded", file.FileName)
		case components.UploadStreamSSEEventEventFileFailed:
			if file.Reason == "DUPLICATE_NAME" {
				// Running this again with the same files is fine: they are already there.
				fmt.Println("  already in the knowledge base, skipped:", file.FileName)
				continue
			}
			failed++
			fmt.Printf("  failed   %s: %s\n", file.FileName, strings.Join(file.Errors, "; "))
		case components.UploadStreamSSEEventEventError:
			log.Fatalf("upload: %s", data)
		}
	}
	if err := stream.Err(); err != nil {
		log.Fatalf("upload: %v", err)
	}
	if failed > 0 {
		log.Fatalf("%d of %d file(s) failed to upload", failed, len(files))
	}
	return names
}

// waitUntilIndexed polls the knowledge base until every uploaded file is indexed, so a
// search right after this finds them.
func waitUntilIndexed(ctx context.Context, client *pipeshub.Pipeshub, kbID string, names []string) {
	fmt.Print("Waiting for indexing")
	flattened, records, limit := true, "record", int64(100)
	deadline := time.Now().Add(indexTimeout)
	for {
		res, err := client.KnowledgeBase.GetKnowledgeHubChildNodes(ctx, operations.GetKnowledgeHubChildNodesRequest{
			ParentType: operations.ParentTypeApp, ParentID: kbID, Flattened: &flattened, NodeTypes: &records, Limit: &limit,
		})
		if err != nil {
			log.Fatalf("\nlist records: %v", err)
		}
		status := map[string]string{}
		if res.KnowledgeHubNodesResponse != nil {
			for _, n := range res.KnowledgeHubNodesResponse.Items {
				if n.IndexingStatus != nil {
					status[n.Name] = *n.IndexingStatus
				}
			}
		}
		done := 0
		for _, name := range names {
			// PipesHub may store the name with or without its extension.
			s := status[name]
			if s == "" {
				s = status[strings.TrimSuffix(name, filepath.Ext(name))]
			}
			switch s {
			case "COMPLETED":
				done++
			case "", "NOT_STARTED", "QUEUED", "IN_PROGRESS":
			default:
				log.Fatalf("\n%s did not index: %s", name, s)
			}
		}
		if done == len(names) {
			fmt.Printf("\nIndexed %d file(s).\n", done)
			return
		}
		if time.Now().After(deadline) {
			log.Fatalf("\nindexing did not finish in %s (%d of %d done)", indexTimeout, done, len(names))
		}
		fmt.Print(".")
		time.Sleep(5 * time.Second)
	}
}
