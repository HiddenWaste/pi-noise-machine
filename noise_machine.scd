// =====================================================================
// HEADLESS PI NOISE MACHINE: BACKEND PoC
// =====================================================================

// 1. Server Configuration & Clean Boot
s.options.numOutputBusChannels = 2; // Force stereo for headphones/aux
s.options.localBufSize = 65536;     // Extra buffer head-room for reverbs

s.waitForBoot({
    "--- SuperCollider Audio Server Booted Successfully ---".postln;

    // 2. Audio Architecture (Your Ambient Sea Waves Synth)
    SynthDef(\sea_waves, {
        |out=0, pan=0.5, amp=0.4, lpf=2000, atk=0.5, rel=3|
        var sig, env;

        sig = BrownNoise.ar(amp);
        sig = FreeVerb.ar(sig, 0.5, 0.6, 0.3);
        sig = LPF.ar(sig, lpf);

        // doneAction: 2 ensures completed synths free themselves from RAM
        env = EnvGen.ar(Env([0, 0.8, 1, 0.25, 0], [atk, atk, rel * 0.33, rel * 0.66]), doneAction: 2);

        sig = sig * env * amp;
        sig = Pan2.ar(sig, Line.kr((-1) * pan, pan, rel));
        
        Out.ar(out, sig);
    }).add;

    // Synchronize with the server to ensure SynthDef is loaded before patterns use it
    s.sync;
    "--- SynthDefs Loaded ---".postln;

    // 3. Define the Pattern Routine (Instantiated but not playing automatically)
    Pbindef(\slow_waves,
        \instrument, \sea_waves,
        \rel, Pxrand([6, 8, 10], inf),
        \dur, Pwrand([6, 8], [0.6, 0.4], inf),
        \amp, Pwhite(0.2, 0.35, inf), // Slightly padded back for safety
        \pan, Pwhite(-0.7, 0.7, inf),
        \lpf, Pxrand([2000, 3000, 4000, 1500], inf)
    );

    // 4. OSC Control Webhooks (Listening on default language port 57120)
    
    // Play Trigger
    OSCdef(\play_trigger, {
        arg msg, time, addr, recvPort;
        "OSC Received: /machine/play -> Starting Waves".postln;
        
        // Quantize to 0 ensures instant playback response rather than waiting for clock cycles
        Pbindef(\slow_waves).play(quant: 0);
    }, '/machine/play');

    // Stop Trigger
    OSCdef(\stop_trigger, {
        arg msg, time, addr, recvPort;
        "OSC Received: /machine/stop -> Silencing Waves".postln;
        
        Pbindef(\slow_waves).stop;
    }, '/machine/stop');

    "--- OSC System Listening on Port 57120 ---".postln;
});
