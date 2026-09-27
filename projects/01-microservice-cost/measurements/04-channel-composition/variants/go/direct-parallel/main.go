// The direct call graph with each level evaluated in parallel: composition 1,
// medium effort.
package main

import "channelcomposition/graph"

func main() { graph.Run(graph.DirectParallel) }
