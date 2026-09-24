// Command fingerprint records the machine state that a measurement depends on.
// Every result file carries one. A number without its fingerprint cannot be
// compared to anything later.
package main

import (
	"encoding/json"
	"os"
	"os/exec"
	"runtime"
	"strings"
	"time"
)

type Fingerprint struct {
	Recorded   string            `json:"recorded"`
	Host       string            `json:"host"`
	Kernel     string            `json:"kernel"`
	CPUModel   string            `json:"cpu_model"`
	CPUs       int               `json:"cpus"`
	Governor   string            `json:"governor"`
	Turbo      string            `json:"turbo"`
	LoadAvg    string            `json:"load_avg"`
	Toolchains map[string]string `json:"toolchains"`
}

// readTrim returns the trimmed contents of path, or "" when it is unreadable.
// An absent sysfs knob is normal, not an error: containers and non-Intel hosts
// simply do not publish some of them.
func readTrim(path string) string {
	b, err := os.ReadFile(path)
	if err != nil {
		return ""
	}
	return strings.TrimSpace(string(b))
}

// field pulls one "key : value" line out of /proc-style text.
func field(text, key string) string {
	for _, line := range strings.Split(text, "\n") {
		name, value, found := strings.Cut(line, ":")
		if found && strings.TrimSpace(name) == key {
			return strings.TrimSpace(value)
		}
	}
	return ""
}

// version runs a tool's version command. A missing tool records "absent" so
// the gap is visible in the result rather than silently omitted.
func version(name string, args ...string) string {
	out, err := exec.Command(name, args...).CombinedOutput()
	if err != nil {
		return "absent"
	}
	line, _, _ := strings.Cut(strings.TrimSpace(string(out)), "\n")
	return strings.TrimSpace(line)
}

// turboState reads whichever boost knob this CPU publishes. Intel inverts the
// sense, so both are normalised to on/off here.
func turboState() string {
	if v := readTrim("/sys/devices/system/cpu/intel_pstate/no_turbo"); v != "" {
		if v == "0" {
			return "on"
		}
		return "off"
	}
	if v := readTrim("/sys/devices/system/cpu/cpufreq/boost"); v != "" {
		if v == "1" {
			return "on"
		}
		return "off"
	}
	return "unknown"
}

func main() {
	host, _ := os.Hostname()
	f := Fingerprint{
		Recorded: time.Now().UTC().Format(time.RFC3339),
		Host:     host,
		Kernel:   readTrim("/proc/sys/kernel/osrelease"),
		CPUModel: field(readTrim("/proc/cpuinfo"), "model name"),
		CPUs:     runtime.NumCPU(),
		Governor: readTrim("/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor"),
		Turbo:    turboState(),
		LoadAvg:  readTrim("/proc/loadavg"),
		Toolchains: map[string]string{
			"go":     version("go", "version"),
			"node":   version("node", "--version"),
			"rustc":  version("rustc", "--version"),
			"java":   version("java", "-version"),
			"python": version("python3", "--version"),
			"gcc":    version("gcc", "--version"),
		},
	}
	enc := json.NewEncoder(os.Stdout)
	enc.SetIndent("", "  ")
	if err := enc.Encode(f); err != nil {
		os.Exit(1)
	}
}
