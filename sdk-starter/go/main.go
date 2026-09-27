// Search your company's knowledge, then ask a question and stream a cited answer.
//
// Usage:
//
//	export PIPESHUB_URL=http://localhost:3000
//	export PIPESHUB_BEARER_AUTH=<personal access token>
//	go run . "what's our on-call policy?"
package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"strings"
	"time"

	pipeshub "github.com/pipeshub-ai/pipeshub-sdk-go"
	"github.com/pipeshub-ai/pipeshub-sdk-go/models/components"
)

func main() {
	query := strings.Join(os.Args[1:], " ")
	if query == "" {
		query = "what's our on-call policy?"
	}
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
		// The SDK's default client gives up after 60s, which a streamed answer can outlast.
		pipeshub.WithClient(&http.Client{Timeout: 3 * time.Minute}),
		pipeshub.WithSecurity(components.Security{BearerAuth: pipeshub.Pointer(token)}),
	)
	ctx := context.Background()
	search(ctx, client, query)
	ask(ctx, client, query)
}

// search runs a semantic search: ranked, permission-filtered records with their source.
func search(ctx context.Context, client *pipeshub.Pipeshub, query string) {
	fmt.Printf("\n== Search: %s\n\n", query)
	limit := int64(5)
	res, err := client.SemanticSearch.Search(ctx, components.SemanticSearchRequest{Query: query, Limit: &limit})
	if err != nil {
		log.Fatalf("search: %v", err)
	}
	var hits []components.SemanticSearchHit
	if res.SemanticSearchExecuteResponse != nil {
		hits = res.SemanticSearchExecuteResponse.SearchResponse.SearchResults
	}
	if len(hits) == 0 {
		fmt.Println("  No results. Connect a source or upload documents to a knowledge base first.")
		return
	}
	// Hits are per chunk, so the same record can appear several times; show each record once, best first.
	seen := map[string]bool{}
	shown := 0
	for _, hit := range hits {
		meta := hit.Metadata
		if meta == nil {
			meta = &components.SemanticSearchHitMetadata{}
		}
		id, _ := meta.RecordID.GetOrZero()
		if seen[id] {
			continue
		}
		seen[id] = true
		shown++
		name, _ := meta.RecordName.GetOrZero()
		if name == "" {
			name = "(untitled)"
		}
		source, _ := meta.ConnectorName.GetOrZero()
		if source == "" {
			source = "knowledge base"
		}
		score := "-"
		if s, ok := hit.Score.GetOrZero(); ok {
			score = fmt.Sprintf("%.2f", s)
		}
		fmt.Printf("  %d. %s  [%s, score %s]\n", shown, name, source, score)
		if url, _ := meta.WebURL.GetOrZero(); url != "" {
			fmt.Printf("     %s\n", url)
		}
	}
}

// ask starts a conversation, streams the answer token by token, then lists its citations.
func ask(ctx context.Context, client *pipeshub.Pipeshub, query string) {
	fmt.Print("\n== Answer\n\n")
	mode := components.ConversationStreamRequestChatModeInternalSearch
	res, err := client.Conversations.StreamChat(ctx, components.ConversationStreamRequest{Query: query, ChatMode: mode})
	if err != nil {
		log.Fatalf("ask: %v", err)
	}
	stream := res.ConversationStreamSSEEvent
	defer stream.Close()
	for stream.Next() {
		ev := stream.Value()
		if ev == nil || ev.Event == nil || ev.Data == nil {
			continue
		}
		switch *ev.Event {
		case components.ConversationStreamSSEEventEventTextMessageContent:
			var p struct {
				Delta string `json:"delta"`
			}
			_ = json.Unmarshal([]byte(*ev.Data), &p)
			fmt.Print(p.Delta)
		case components.ConversationStreamSSEEventEventRunFinished:
			fmt.Print("\n\n")
			printCitations(*ev.Data)
		case components.ConversationStreamSSEEventEventRunError:
			var p struct {
				Message string `json:"message"`
			}
			_ = json.Unmarshal([]byte(*ev.Data), &p)
			if p.Message == "" {
				p.Message = "stream failed"
			}
			fmt.Printf("\n\nError: %s\n", p.Message)
		}
	}
	if err := stream.Err(); err != nil {
		log.Fatalf("ask: %v", err)
	}
}

// printCitations reads RUN_FINISHED: it carries the saved conversation, whose last message holds the citations.
func printCitations(data string) {
	var finished struct {
		Result struct {
			Conversation struct {
				Messages []struct {
					Citations []struct {
						CitationID   string `json:"citationId"`
						Metadata     map[string]any
						CitationData struct {
							Metadata map[string]any `json:"metadata"`
						} `json:"citationData"`
					} `json:"citations"`
				} `json:"messages"`
			} `json:"conversation"`
		} `json:"result"`
	}
	if err := json.Unmarshal([]byte(data), &finished); err != nil {
		return
	}
	msgs := finished.Result.Conversation.Messages
	if len(msgs) == 0 || len(msgs[len(msgs)-1].Citations) == 0 {
		return
	}
	fmt.Print("== Sources\n\n")
	seen := map[string]bool{}
	for _, c := range msgs[len(msgs)-1].Citations {
		meta := c.CitationData.Metadata
		if meta == nil {
			meta = c.Metadata
		}
		name := str(meta, "recordName")
		if name == "" {
			name = c.CitationID
		}
		if seen[name] {
			continue
		}
		seen[name] = true
		source := str(meta, "connectorName")
		if source == "" {
			source = str(meta, "connector")
		}
		if source == "" {
			source = "knowledge base"
		}
		line := fmt.Sprintf("  - %s  [%s]", name, source)
		if url := str(meta, "webUrl"); url != "" {
			line += "  " + url
		}
		fmt.Println(line)
	}
}

func str(m map[string]any, key string) string {
	s, _ := m[key].(string)
	return s
}
