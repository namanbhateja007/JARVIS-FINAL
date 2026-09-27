const intro = document.getElementById("intro");
const app = document.getElementById("app");
const introText = document.getElementById("introText");
const systemStatus = document.getElementById("systemStatus");
const coreState = document.getElementById("coreState");
const mainText = document.getElementById("mainText");
const subText = document.getElementById("subText");
const microText = document.getElementById("microText");
const commandText = document.getElementById("commandText");
const coreWrap = document.getElementById("coreWrap");
const listenBtn = document.getElementById("listenBtn");
const visualizer = document.getElementById("visualizer");
const activityBars = document.getElementById("activityBars");
const clock = document.getElementById("clock");


/* =========================
   ACTIVITY BARS
========================= */

const bars = [];

for (let i = 0; i < 42; i++) {
  const bar = document.createElement("i");
  activityBars.appendChild(bar);
  bars.push(bar);
}


/* =========================
   VISUALIZER SPOKES
========================= */

const spokeCount = 96;
const spokes = [];

for (let i = 0; i < spokeCount; i++) {
  const spoke = document.createElement("span");
  visualizer.appendChild(spoke);
  spokes.push(spoke);
}


/* =========================
   SLEEP
========================= */

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}


/* =========================
   INTRO ANIMATION
========================= */

async function introSequence() {
  const greetings = [
    "Hi there.",
    "Good to see you.",
    "Initializing.",
    "JARVIS online."
  ];

  let index = 0;

  const timer = setInterval(() => {
    index = (index + 1) % greetings.length;

    introText.style.opacity = "0";
    introText.style.transform = "translateY(8px)";

    setTimeout(() => {
      introText.textContent = greetings[index];
      introText.style.opacity = "1";
      introText.style.transform = "translateY(0)";
    }, 280);

  }, 1300);

  await sleep(4300);

  clearInterval(timer);

  intro.classList.add("exit");
  app.classList.remove("hidden");

  setTimeout(() => {
    intro.remove();
  }, 1400);
}


/* =========================
   CLOCK
========================= */

function updateClock() {
  clock.textContent = new Date().toLocaleTimeString([], {
    hour12: false
  });
}


/* =========================
   JARVIS STATES
========================= */

function setState(state) {

  document.body.classList.toggle(
    "active",
    state !== "standby"
  );

  const states = {

    listening: [
      "LISTENING",
      "LISTEN",
      "VOICE INPUT DETECTED",
      "I'm listening.",
      "Tell me what you need.",
      "Listening for your command…"
    ],

    thinking: [
      "PROCESSING",
      "THINK",
      "JARVIS IS THINKING",
      "Working on it.",
      "Processing your request…",
      "Processing command…"
    ],

    speaking: [
      "SPEAKING",
      "TALK",
      "VOICE OUTPUT",
      "Here you go.",
      "JARVIS is responding.",
      "Playing voice response…"
    ],

    standby: [
      "STANDBY",
      "READY",
      "VOICE INTERFACE ONLINE",
      "How can I help?",
      'Say <span>“Jarvis”</span> to begin.',
      "Waiting for voice input…"
    ]

  };

  const s = states[state] || states.standby;

  systemStatus.textContent = s[0];
  coreState.textContent = s[1];
  microText.textContent = s[2];
  mainText.textContent = s[3];
  subText.innerHTML = s[4];
  commandText.textContent = s[5];
}


/* =========================
   VISUALIZER
========================= */

let audioLevel = 0.03;
let targetLevel = 0.03;
let demoMode = false;

function renderVisuals() {

  if (demoMode) {
    targetLevel =
      0.12 +
      Math.abs(Math.sin(Date.now() / 250)) * 0.65;
  }

  audioLevel +=
    (targetLevel - audioLevel) * 0.13;


  /* Central core */

  coreWrap.style.transform =
    `scale(${1 + audioLevel * 0.38})`;


  /* Outer spokes */

  spokes.forEach((spoke, i) => {

    const angle =
      (360 / spokeCount) * i;

    const wave =
      Math.abs(
        Math.sin(
          Date.now() / (120 + (i % 7) * 20) +
          i * 0.7
        )
      );

    const variation =
      wave * audioLevel;

    const length =
      145 +
      (i % 5) * 4 +
      variation * 90;

    spoke.style.height =
      `${12 + variation * 36}px`;

    spoke.style.opacity =
      0.14 + variation * 0.95;

    spoke.style.transform =
      `translate(-50%,-100%)
       rotate(${angle}deg)
       translateY(-${length}px)`;
  });


  /* Bottom activity bars */

  bars.forEach((bar, i) => {

    const wave =
      Math.abs(
        Math.sin(
          Date.now() / (90 + i * 7) + i
        )
      );

    bar.style.height =
      `${3 + wave * (7 + audioLevel * 15)}px`;
  });


  requestAnimationFrame(renderVisuals);
}


/* =========================
   BACKEND STATE SYNC
========================= */

async function syncBackendState() {

  try {

    const res = await fetch(
      "/api/state",
      {
        cache: "no-store"
      }
    );

    if (!res.ok) return;

    const data = await res.json();

    if (data.state) {
      setState(data.state);
    }

    if (typeof data.audio_level === "number") {

      targetLevel =
        Math.max(
          0,
          Math.min(1, data.audio_level)
        );
    }

    if (data.command) {
      commandText.textContent =
        data.command;
    }

  } catch (_) {

    /*
      Opening index.html directly
      still works in demo mode.
    */

  }
}


/* =========================
   BROWSER SPEECH RECOGNITION
========================= */

const SpeechRecognition =
  window.SpeechRecognition ||
  window.webkitSpeechRecognition;

let recognition = null;

if (SpeechRecognition) {

  recognition = new SpeechRecognition();

  recognition.lang = "en-IN";

  recognition.continuous = false;

  recognition.interimResults = false;


  /* Microphone started */

  recognition.onstart = () => {

    console.log(
      "JARVIS microphone started"
    );

    demoMode = true;

    setState("listening");
  };


  /* Voice converted to text */

  recognition.onresult = (event) => {

    const command =
      event.results[0][0].transcript;

    console.log(
      "You said:",
      command
    );

    commandText.textContent =
      command;

    demoMode = false;

    /*
      Send the recognized command
      to Gemini.
    */

    askJarvis(command);
  };


  /* Recognition error */

  recognition.onerror = (event) => {

    console.error(
      "Speech recognition error:",
      event.error
    );

    demoMode = false;

    targetLevel = 0.03;

    setState("standby");

    commandText.textContent =
      "Microphone error: " +
      event.error;
  };


  /* Microphone stopped */

  recognition.onend = () => {

    console.log(
      "JARVIS microphone stopped"
    );

    demoMode = false;
  };

} else {

  console.error(
    "Speech Recognition is not supported in this browser."
  );
}


/* =========================
   LISTEN BUTTON
========================= */

listenBtn.addEventListener(
  "click",
  () => {

    if (!recognition) {

      commandText.textContent =
        "Speech recognition is not supported.";

      return;
    }

    /*
      Stop any currently playing
      JARVIS voice.
    */

    window.speechSynthesis.cancel();

    try {

      recognition.start();

    } catch (error) {

      console.error(
        "Could not start microphone:",
        error
      );
    }
  }
);


/* =========================
   JARVIS → GEMINI
========================= */

async function askJarvis(command) {

  setState("thinking");

  commandText.textContent =
    command;

  try {

    const response = await fetch(
      "https://jarvis-final-ykke.onrender.com/chat",
      {
        method: "POST",

        headers: {
          "Content-Type":
            "application/json"
        },

        body: JSON.stringify({
          command: command
        })
      }
    );


    const data =
      await response.json();


    if (!data.success) {

      throw new Error(
        data.error ||
        "JARVIS backend error"
      );
    }


    /*
      Display Gemini's answer.
    */

    commandText.textContent =
      data.response;


    /*
      JARVIS starts speaking.
    */

    setState("speaking");


    const speech =
      new SpeechSynthesisUtterance(
        data.response
      );

    speech.rate = 0.9;


    speech.onend = () => {

      targetLevel = 0.03;

      setState("standby");
    };


    window.speechSynthesis.cancel();

    window.speechSynthesis.speak(
      speech
    );


  } catch (error) {

    console.error(
      "JARVIS CONNECTION ERROR:",
      error
    );

    setState("standby");

    commandText.textContent =
      "ERROR: " +
      error.message;
  }
}


/* =========================
   GLOBAL JARVIS UI
========================= */

window.jarvisUI = {

  setState,

  showCommand(command) {
    commandText.textContent =
      command;
  },

  setAudioLevel(level) {

    targetLevel =
      Math.max(
        0,
        Math.min(
          1,
          Number(level) || 0
        )
      );
  }
};


/* =========================
   GLOBAL ASK FUNCTION
========================= */

window.askJarvis = askJarvis;


/* =========================
   START EVERYTHING
========================= */

setInterval(
  updateClock,
  1000
);

setInterval(
  syncBackendState,
  100
);

updateClock();

renderVisuals();

introSequence();