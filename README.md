<!--<a href="https://livekit.io/">
  <img src="./.github/assets/livekit-mark.png" alt="LiveKit logo" width="100" height="100">
</a> -->

# LiveKit + Cartesia Python Voice Agent

<p>
  <a href="https://cloud.livekit.io/projects/p_/sandbox"><strong>Deploy a sandbox app</strong></a>
  •
  <a href="https://docs.livekit.io/agents/overview/">LiveKit Agents Docs</a>
  •
  <a href="https://livekit.io/cloud">LiveKit Cloud</a>
  •
  <a href="https://blog.livekit.io/">Blog</a>
</p>

A basic example of a voice agent using LiveKit with Cartesia.

## Dev Setup

Clone the repository and install dependencies to a virtual environment:

```console
cd cartesia-livekit-voice-agent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Set up the environment by copying `.env.example` to `.env.local` and filling in the required values:

- `LIVEKIT_URL`
- `LIVEKIT_API_KEY`
- `LIVEKIT_API_SECRET`
- `OPENAI_API_KEY`
- `CARTESIA_API_KEY`

You can also do this automatically using the LiveKit CLI:

```console
lk app env
```

The easiest and quickest way to chat with the agent is via the console:

```console
python3 agent.py console
```

You can also run it with a frontend. For that, run the agent:

```console
python3 agent.py dev
```

Then use a frontend application to communicate with the agent. Some examples of frontends are available in [livekit-examples](https://github.com/livekit-examples/). You can also create your own frontend following one of the [client quickstarts](https://docs.livekit.io/realtime/quickstarts/), or test instantly against one of LiveKit's hosted [Sandbox](https://cloud.livekit.io/projects/p_/sandbox) frontends.
