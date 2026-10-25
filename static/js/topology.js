/**
 * AI-NIDS - Network Topology Interactive Graph
 * Built with vis-network (OLED Monochrome & Signature Red theme)
 */

let topoNetwork = null;
let topoNodesDataSet = null;
let topoEdgesDataSet = null;
let topoRawData = null;
let topoPhysicsEnabled = true;
let topoStreamPaused = false;
let topoCurrentFilter = "ALL";
let selectedNodeData = null;

const TOPO_COLORS = {
    attacker: {
        background: "#d71920",
        border: "#ff4d4d",
        highlight: { background: "#ff4d4d", border: "#ffffff" },
        hover: { background: "#ff4d4d", border: "#ffffff" }
    },
    target: {
        background: "#082830",
        border: "#00f0ff",
        highlight: { background: "#00f0ff", border: "#ffffff" },
        hover: { background: "#00f0ff", border: "#ffffff" }
    },
    internal: {
        background: "#1c1c1c",
        border: "#e5e5e5",
        highlight: { background: "#333333", border: "#ffffff" },
        hover: { background: "#333333", border: "#ffffff" }
    },
    external: {
        background: "#121212",
        border: "#555555",
        highlight: { background: "#252525", border: "#888888" },
        hover: { background: "#252525", border: "#888888" }
    }
};

function formatNodeItem(node) {
    let colorConfig = TOPO_COLORS.external;
    let shape = "dot";
    let size = 16;
    let borderWidth = 2;

    if (node.node_type === "ATTACKER") {
        colorConfig = TOPO_COLORS.attacker;
        shape = "diamond";
        size = 24;
        borderWidth = 3;
    } else if (node.node_type === "TARGET_SERVER") {
        colorConfig = TOPO_COLORS.target;
        shape = "dot";
        size = 26;
        borderWidth = 3;
    } else if (node.node_type === "INTERNAL_HOST") {
        colorConfig = TOPO_COLORS.internal;
        shape = "dot";
        size = 18;
    }

    const shortLabel = node.label.length > 18 ? node.label.slice(0, 16) + ".." : node.label;

    return {
        id: node.id,
        label: `${shortLabel}${node.threat_count > 0 ? ' [!]' : ''}`,
        title: `${node.id} (${node.node_type})\nFlows: ${node.flow_count} | Packets: ${node.packet_volume}\nThreats: ${node.threat_count}`,
        color: colorConfig,
        shape: shape,
        size: size,
        borderWidth: borderWidth,
        font: {
            color: node.node_type === "ATTACKER" ? "#ff4d4d" : (node.node_type === "TARGET_SERVER" ? "#00f0ff" : "#dddddd"),
            face: "JetBrains Mono, monospace",
            size: 11,
            vadjust: -24
        },
        shadow: node.node_type === "ATTACKER" ? { enabled: true, color: "rgba(215, 25, 32, 0.5)", size: 14 } : false,
        rawNode: node
    };
}

function formatEdgeItem(edge) {
    const isAttack = edge.is_attack;
    return {
        id: edge.id,
        from: edge.from,
        to: edge.to,
        arrows: { to: { enabled: true, scaleFactor: 0.6 } },
        color: {
            color: isAttack ? "#d71920" : "rgba(255, 255, 255, 0.22)",
            highlight: isAttack ? "#ff4d4d" : "#ffffff",
            hover: isAttack ? "#ff4d4d" : "#ffffff",
            opacity: isAttack ? 0.95 : 0.6
        },
        width: isAttack ? 2.5 : Math.min(4, Math.max(1, edge.packet_count / 15)),
        dashes: isAttack,
        smooth: { type: "curvedCW", roundness: 0.15 },
        title: `${edge.protocol}: ${edge.from} -> ${edge.to}\nPrediction: ${edge.prediction}\nPackets: ${edge.packet_count} | Bytes: ${edge.byte_count}`,
        rawEdge: edge
    };
}

async function fetchTopologyData() {
    try {
        const response = await fetch("/api/topology");
        const data = await response.json();
        topoRawData = data;

        // Update metric indicators
        setText("topoTotalNodes", data.total_nodes);
        setText("topoTotalEdges", data.total_edges);
        setText("topoAttackEdges", data.attack_edges);

        applyTopologyFilter(topoCurrentFilter);
    } catch (err) {
        console.error("Error fetching topology data:", err);
    }
}

function applyTopologyFilter(filter) {
    if (!topoRawData) return;
    topoCurrentFilter = filter;

    let filteredNodes = topoRawData.nodes;
    let filteredEdges = topoRawData.edges;

    if (filter === "ATTACKS") {
        const attackIps = new Set();
        filteredEdges = topoRawData.edges.filter(e => e.is_attack);
        filteredEdges.forEach(e => {
            attackIps.add(e.from);
            attackIps.add(e.to);
        });
        filteredNodes = topoRawData.nodes.filter(n => attackIps.has(n.id) || n.node_type === "ATTACKER");
    } else if (filter === "INTERNAL") {
        filteredNodes = topoRawData.nodes.filter(n => n.is_private);
        const internalIps = new Set(filteredNodes.map(n => n.id));
        filteredEdges = topoRawData.edges.filter(e => internalIps.has(e.from) || internalIps.has(e.to));
    }

    const formattedNodes = filteredNodes.map(formatNodeItem);
    const formattedEdges = filteredEdges.map(formatEdgeItem);

    if (!topoNetwork) {
        initTopologyNetwork(formattedNodes, formattedEdges);
    } else {
        topoNodesDataSet.clear();
        topoNodesDataSet.add(formattedNodes);
        topoEdgesDataSet.clear();
        topoEdgesDataSet.add(formattedEdges);
    }
}

function initTopologyNetwork(nodes, edges) {
    const container = document.getElementById("networkTopologyCanvas");
    if (!container) return;

    topoNodesDataSet = new vis.DataSet(nodes);
    topoEdgesDataSet = new vis.DataSet(edges);

    const data = {
        nodes: topoNodesDataSet,
        edges: topoEdgesDataSet
    };

    const options = {
        physics: {
            enabled: topoPhysicsEnabled,
            solver: "barnesHut",
            barnesHut: {
                gravitationalConstant: -2800,
                centralGravity: 0.25,
                springLength: 130,
                springConstant: 0.04,
                damping: 0.09,
                avoidOverlap: 0.3
            },
            stabilization: {
                iterations: 80,
                updateInterval: 25
            }
        },
        interaction: {
            hover: true,
            tooltipDelay: 150,
            zoomView: true,
            dragView: true,
            multiselect: false
        }
    };

    topoNetwork = new vis.Network(container, data, options);

    // Event: Node Click
    topoNetwork.on("selectNode", function (params) {
        if (!params.nodes.length) return;
        const nodeId = params.nodes[0];
        const nodeItem = topoNodesDataSet.get(nodeId);
        if (nodeItem && nodeItem.rawNode) {
            showTopologySidebar(nodeItem.rawNode);
        }
    });

    // Event: Deselect
    topoNetwork.on("deselectNode", function () {
        closeTopologySidebar();
    });

    // Event: Edge Click -> Open Flow Inspector Modal!
    topoNetwork.on("selectEdge", function (params) {
        // If a node is selected, don't trigger edge inspection
        if (params.nodes && params.nodes.length > 0) return;
        if (!params.edges.length) return;

        const edgeId = params.edges[0];
        const edgeItem = topoEdgesDataSet.get(edgeId);
        if (edgeItem && edgeItem.rawEdge && edgeItem.rawEdge.flow_id) {
            // Populate cached flow if available
            if (typeof openFlowInspector === "function") {
                const raw = edgeItem.rawEdge;
                window.cachedFlows.set(raw.flow_id, {
                    id: raw.flow_id,
                    timestamp: "Recent Flow",
                    source_ip: raw.from,
                    destination_ip: raw.to,
                    protocol: raw.protocol,
                    packet_count: raw.packet_count,
                    byte_count: raw.byte_count,
                    prediction: raw.prediction,
                    confidence: raw.confidence,
                    data_source: "TOPOLOGY"
                });
                openFlowInspector(raw.flow_id, "flow");
            }
        }
    });
}

function showTopologySidebar(node) {
    selectedNodeData = node;
    const sidebar = document.getElementById("topologySidebar");
    if (!sidebar) return;

    setText("sidebarNodeIp", node.id);
    setText("sidebarNodeFlows", node.flow_count);
    setText("sidebarNodePackets", node.packet_volume);
    setText("sidebarNodeThreats", node.threat_count);

    const badge = document.getElementById("sidebarNodeRoleBadge");
    if (badge) {
        badge.className = "badge";
        if (node.node_type === "ATTACKER") {
            badge.className = "badge-attack";
            badge.textContent = "MALICIOUS ATTACKER";
        } else if (node.node_type === "TARGET_SERVER") {
            badge.className = "badge-benign";
            badge.style.color = "#00f0ff";
            badge.textContent = "INTERNAL TARGET / SERVER";
        } else if (node.node_type === "INTERNAL_HOST") {
            badge.className = "badge-benign";
            badge.textContent = "INTERNAL NETWORK ASSET";
        } else {
            badge.className = "badge-benign";
            badge.textContent = "EXTERNAL CLIENT";
        }
    }

    const threatCountEl = document.getElementById("sidebarNodeThreats");
    if (threatCountEl) {
        threatCountEl.className = node.threat_count > 0 ? "text-danger fw-bold" : "text-white fw-bold";
    }

    sidebar.classList.remove("d-none");
}

function closeTopologySidebar() {
    selectedNodeData = null;
    const sidebar = document.getElementById("topologySidebar");
    if (sidebar) sidebar.classList.add("d-none");
}

function copySidebarIp() {
    if (selectedNodeData && selectedNodeData.id) {
        copyToClipboard(selectedNodeData.id, "Host IP");
    }
}

function setTopologyFilter(filter) {
    ["btnFilterAll", "btnFilterAttacks", "btnFilterInternal"].forEach(id => {
        document.getElementById(id)?.classList.remove("active");
    });

    if (filter === "ALL") document.getElementById("btnFilterAll")?.classList.add("active");
    if (filter === "ATTACKS") document.getElementById("btnFilterAttacks")?.classList.add("active");
    if (filter === "INTERNAL") document.getElementById("btnFilterInternal")?.classList.add("active");

    applyTopologyFilter(filter);
    if (typeof showThreatToast === "function") {
        showThreatToast("TOPOLOGY FILTER", `Displaying: ${filter} network nodes.`, false);
    }
}

function togglePhysics() {
    topoPhysicsEnabled = !topoPhysicsEnabled;
    const btn = document.getElementById("btnTogglePhysics");
    if (topoNetwork) {
        topoNetwork.setOptions({ physics: { enabled: topoPhysicsEnabled } });
    }
    if (btn) {
        btn.textContent = `⚛ PHYSICS: ${topoPhysicsEnabled ? 'ON' : 'OFF'}`;
        if (!topoPhysicsEnabled) {
            btn.classList.add("btn-stream-paused");
        } else {
            btn.classList.remove("btn-stream-paused");
        }
    }
}

function resetTopologyView() {
    if (topoNetwork) {
        topoNetwork.fit({
            animation: {
                duration: 800,
                easingFunction: "easeInOutQuad"
            }
        });
    }
}

function toggleTopologyPause() {
    topoStreamPaused = !topoStreamPaused;
    const btn = document.getElementById("btnPauseTopology");
    if (btn) {
        if (topoStreamPaused) {
            btn.classList.add("btn-stream-paused");
            btn.innerHTML = '<span>▶</span> <span>RESUME FEED</span>';
            if (typeof showThreatToast === "function") {
                showThreatToast("FEED PAUSED", "Topology updates frozen for analysis.", false);
            }
        } else {
            btn.classList.remove("btn-stream-paused");
            btn.innerHTML = '<span>⏸</span> <span>PAUSE FEED</span>';
            fetchTopologyData();
            if (typeof showThreatToast === "function") {
                showThreatToast("FEED RESUMED", "Live topology auto-refresh re-enabled.", false);
            }
        }
    }
}

// Bind search input to focus on matching node
document.addEventListener("DOMContentLoaded", () => {
    const searchInput = document.getElementById("topoSearchInput");
    if (searchInput) {
        searchInput.addEventListener("input", (e) => {
            const query = e.target.value.toLowerCase().trim();
            if (!query || !topoNodesDataSet || !topoNetwork) return;

            const allNodes = topoNodesDataSet.get();
            const match = allNodes.find(n => n.id.toLowerCase().includes(query) || n.label.toLowerCase().includes(query));
            if (match) {
                topoNetwork.focus(match.id, {
                    scale: 1.3,
                    animation: { duration: 600, easingFunction: "easeInOutQuad" }
                });
                topoNetwork.selectNodes([match.id]);
                if (match.rawNode) showTopologySidebar(match.rawNode);
            }
        });
    }

    // Initial fetch
    fetchTopologyData();

    // Auto-refresh every 4 seconds unless paused
    setInterval(() => {
        if (!topoStreamPaused) {
            fetchTopologyData();
        }
    }, 4000);
});
