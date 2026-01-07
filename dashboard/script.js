import { initializeApp } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js";
import {
  getFirestore,
  collection,
  query,
  orderBy,
  limit,
  onSnapshot
} from "https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore.js";

import { firebaseConfig } from "./config.js";


const app = initializeApp(firebaseConfig);
const db = getFirestore(app);

const logTable = document.getElementById("logTable");
const totalRisks = document.getElementById("totalRisks");
const totalWarnings = document.getElementById("totalWarnings");
const totalCollisions = document.getElementById("totalCollisions");
const heatmapGrid = document.getElementById("heatmapGrid");

/* 🔹 Queries */
const recentLogsQuery = query(
  collection(db, "events"),
  orderBy("timestamp", "desc"),
  limit(20)
);

const allEventsQuery = query(
  collection(db, "events")
);

/* 🔥 Heatmap renderer */
function renderHeatmap(events) {
  heatmapGrid.innerHTML = "";
  const zoneCount = {};

  events.forEach(e => {
    const road = e.road_segment || "Unknown";
    zoneCount[road] = (zoneCount[road] || 0) + 1;
  });

  Object.entries(zoneCount).forEach(([road, count]) => {
    let level = "low";
    if (count > 10) level = "high";
    else if (count > 5) level = "medium";

    const cell = document.createElement("div");
    cell.className = `heatmap-cell ${level}`;
    cell.innerText = road;

    heatmapGrid.appendChild(cell);
  });
}

/* 🔄 Recent 20 logs */
onSnapshot(recentLogsQuery, (snapshot) => {
  logTable.innerHTML = "";

  snapshot.forEach(doc => {
    const d = doc.data();

    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${d.road_segment}</td>
      <td>${d.risk_level}</td>
      <td>${d.warning_issued ? "Yes" : "No"}</td>
      <td>${d.cattle_count ?? "-"}</td>
    `;

    if (d.risk_level === "HIGH") {
      row.style.backgroundColor = "#fee2e2";
    }

    logTable.appendChild(row);
  });
});

/* 🔄 Totals + heatmap */
onSnapshot(allEventsQuery, (snapshot) => {
  let risks = 0;
  let warnings = 0;
  let collisions = 0;
  const allEvents = [];

  snapshot.forEach(doc => {
    const d = doc.data();
    allEvents.push(d);

    risks++;
    if (d.warning_issued) warnings++;
    if (d.collision_detected) collisions++;
  });

  totalRisks.innerText = risks;
  totalWarnings.innerText = warnings;
  totalCollisions.innerText = collisions;

  renderHeatmap(allEvents);
});
