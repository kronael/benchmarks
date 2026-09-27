// Command simd measures the same work unit vectorised. Its twin is ../scalar,
// and the two differ in one argument.
package main

import "benchsimddivto/divto"

func main() {
	divto.Main("simd", divto.Vector)
}
