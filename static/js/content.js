/*
 * Media and links for the anonymous project page.
 * Paths are relative to paper_project/index.html. Leave src empty for a placeholder.
 * Add a file, then set src, e.g. "static/media/revised-20261117/method/overview.png".
 * Images: PNG / JPG / WebP / SVG. Videos: MP4 (H.264 recommended) / WebM.
 * Set codeUrl to the anonymous code repository.
 */
(() => {
  const stateCaption = [
    { text: "Blue", tone: "initial" },
    { text: ": initial state; " },
    { text: "green", tone: "goal" },
    { text: ": predicted goal state." }
  ];

  window.OG_GAUSSIAN_CONTENT = {
    codeUrl: "https://anonymous.4open.science/r/OG-Gaussian_code-47EC/",

    // Static method figure only. Optional: fullsize for a higher-resolution image.
    method: {
      src: "static/media/revised-20261117/method/overview.png?v=64f5a09b85",
      fullsize: "",
      alt: "Overview of the OG-Gaussian framework for object goal-state generation."
    },

    // One comparison image per task. Keep the same sample and view across methods.
    // Add or remove array entries to change the task tabs.
    simulation: [
      {
        id: "pour-water",
        title: "Pour Water",
        media: { type: "image", src: "static/media/simulation/pour-water.webp", alt: "Qualitative comparison on the Pour Water task." },
        caption: stateCaption
      },
      {
        id: "place-teabag",
        title: "Place Teabag",
        media: { type: "image", src: "static/media/simulation/place-teabag.webp", alt: "Qualitative comparison on the Place Teabag task." },
        caption: stateCaption
      },
      {
        id: "place-atomizer",
        title: "Place Atomizer",
        media: { type: "image", src: "static/media/simulation/place-atomizer.webp", alt: "Qualitative comparison on the Place Atomizer task." },
        caption: stateCaption
      },
      {
        id: "lower-cover",
        title: "Lower Cover",
        media: { type: "image", src: "static/media/simulation/lower-cover.webp", alt: "Qualitative comparison on the Lower Cover task." },
        caption: stateCaption
      },
      {
        id: "close-drawer",
        title: "Close Drawer",
        media: { type: "image", src: "static/media/simulation/close-drawer.webp", alt: "Qualitative comparison on the Close Drawer task." },
        caption: stateCaption
      }
    ],

    // Each task shows both executions in separate, side-by-side video players.
    realWorld: [
      {
        id: "pour-water",
        title: "Pour Water",
        media: [
          { type: "video", src: "static/media/revised-20261117/real-world/pour-water.mp4?v=20261118-1", poster: "static/media/revised-20261117/real-world/pour-water.jpg?v=20261118-1", loop: false },
          { type: "video", src: "static/media/revised-20261117-second-executions/real-world/pour-water-2.mp4?v=20261118-1", poster: "static/media/revised-20261117-second-executions/real-world/pour-water-2.jpg?v=20261118-1", loop: false }
        ],
        caption: ""
      },
      {
        id: "place-teabag",
        title: "Place Teabag",
        media: [
          { type: "video", src: "static/media/revised-20261117/real-world/place-teabag.mp4?v=20261118-1", poster: "static/media/revised-20261117/real-world/place-teabag.jpg?v=20261118-1", loop: false },
          { type: "video", src: "static/media/revised-20261117-second-executions/real-world/place-teabag-2.mp4?v=20261118-1", poster: "static/media/revised-20261117-second-executions/real-world/place-teabag-2.jpg?v=20261118-1", loop: false }
        ],
        caption: ""
      },
      {
        id: "place-atomizer",
        title: "Place Atomizer",
        media: [
          { type: "video", src: "static/media/revised-20261117/real-world/place-atomizer.mp4?v=20261118-1", poster: "static/media/revised-20261117/real-world/place-atomizer.jpg?v=20261118-1", loop: false },
          { type: "video", src: "static/media/revised-20261117-second-executions/real-world/place-atomizer-2.mp4?v=20261118-1", poster: "static/media/revised-20261117-second-executions/real-world/place-atomizer-2.jpg?v=20261118-1", loop: false }
        ],
        caption: ""
      },
      {
        id: "lower-cover",
        title: "Lower Cover",
        media: [
          { type: "video", src: "static/media/revised-20261117/real-world/lower-cover.mp4?v=20261118-1", poster: "static/media/revised-20261117/real-world/lower-cover.jpg?v=20261118-1", loop: false },
          { type: "video", src: "static/media/revised-20261117-second-executions/real-world/lower-cover-2.mp4?v=20261118-1", poster: "static/media/revised-20261117-second-executions/real-world/lower-cover-2.jpg?v=20261118-1", loop: false }
        ],
        caption: ""
      },
      {
        id: "close-drawer",
        title: "Close Drawer",
        media: [
          { type: "video", src: "static/media/revised-20261117/real-world/close-drawer.mp4?v=20261118-1", poster: "static/media/revised-20261117/real-world/close-drawer.jpg?v=20261118-1", loop: false },
          { type: "video", src: "static/media/revised-20261117-second-executions/real-world/close-drawer-2.mp4?v=20261118-1", poster: "static/media/revised-20261117-second-executions/real-world/close-drawer-2.jpg?v=20261118-1", loop: false }
        ],
        caption: ""
      }
    ],

    // Successful exploratory demonstrations from the revised demo.
    // Checkpoint training tasks are stated explicitly in each caption.
    toyCases: {
      multipleReferences: {
        type: "video",
        src: "static/media/revised-20261117/exploratory/multiple-references.mp4?v=20261118-1",
        poster: "static/media/revised-20261117/exploratory/multiple-references.jpg?v=20261118-1",
        loop: false,
        alt: "Pouring water into a cup in a scene with multiple reference components.",
        caption: "Pouring water with multiple reference components, using model weights trained on the Pour Water task."
      },
      unseenTasks: {
        type: "video",
        src: "static/media/revised-20261117/exploratory/unseen-tasks.mp4?v=20261118-1",
        poster: "static/media/revised-20261117/exploratory/unseen-tasks.jpg?v=20261118-1",
        loop: false,
        alt: "Placing a kettle in a drawer in an unseen task setting.",
        caption: "Placing a kettle in a drawer, using model weights trained on the Place Teabag task."
      }
    }
  };
})();
