<script>
    import { API_URL } from "../config.js";
    let projects = [];
    let selectedProject = "";

    function fetchProjects() {
        fetch(`${API_URL}/fetch`)
            .then((response) => response.json())
            .then((data) => {
                projects = data.projects;
                console.log("Projects fetched:", data);
            })
            .catch((error) => {
                console.error("Error fetching projects:", error);
                alert("Error fetching projects: " + error);
            });
    }

    function setProject() {
        if (!selectedProject) {
            return;
        }

        fetch(`${API_URL}/set_project`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ project_id: selectedProject }),
        })
            .then((response) => response.json())
            .then((data) => {
                console.log("Project set:", data);
                alert("Project set: " + data.message);
            })
            .catch((error) => {
                console.error("Error setting project:", error);
                alert("Error setting project: " + error);
            });
    }

    $: if (selectedProject) {
        setProject();
    }
</script>

<div class="project-selector">
    <label for="project-select">Select Project:</label>
    <select
        id="project-select"
        bind:value={selectedProject}
        on:focus={fetchProjects}
    >
        <option value="">--Please choose a project--</option>
        {#each projects as project}
            <option value={project.id}>{project.id}</option>
        {/each}
    </select>
</div>

<style>
    .project-selector {
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }

    label {
        font-weight: bold;
        margin-bottom: 0.5rem;
    }

    select {
        background-color: #2a2a2a;
        color: #e0e0e0;
        padding: 0.5rem;
        border: 1px solid #ccc;
        border-radius: 4px;
        font-size: 1rem;
    }
</style>
