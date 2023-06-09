package utils

import "time"

// Fps is a struct that keeps track of the FPS of a stream
type Fps struct {
	OrderedFrames []time.Time
	PrevGet       time.Time
	CachedFps     int
}

// Record is called after each GetImage request to record the timestamp
func (f *Fps) Record() {
	f.OrderedFrames = append(f.OrderedFrames, time.Now())
}

// Get returns the current FPS
// This function returns a new value at most once per second to avoid noise
func (f *Fps) Get() int {
	// Only update once a second
	if time.Since(f.PrevGet) < time.Second {
		return f.CachedFps
	}

	oneSecAgo := time.Now().Add(-time.Second)
	// Evict timestamps greater than one second ago
	i := 0
	for i < len(f.OrderedFrames) && f.OrderedFrames[i].Before(oneSecAgo) {
		i++
	}
	f.OrderedFrames = f.OrderedFrames[i:]

	f.PrevGet = time.Now()
	f.CachedFps = len(f.OrderedFrames)
	return f.CachedFps
}
