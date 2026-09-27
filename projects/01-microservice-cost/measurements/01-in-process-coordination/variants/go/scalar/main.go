// Command scalar measures the work unit without vectorising it. Its twin is
// ../simd, and the two differ in one argument.
package main

import "benchsimddivto/divto"

func main() {
	divto.Main("scalar", divto.Scalar)
}
