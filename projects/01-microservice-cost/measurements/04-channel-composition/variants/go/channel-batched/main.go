// The graph composed of channels, buffered and batched: composition 2, medium
// effort.
package main

import "channelcomposition/graph"

func main() { graph.Run(graph.ChannelBatched) }
