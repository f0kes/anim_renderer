<script>
    import { createEventDispatcher } from "svelte";
    import { API_URL } from "../config.js";

    const dispatch = createEventDispatcher();

    let projectName = "";
    let files = {
        front: null,
        back: null,
        left: null,
        right: null,
    };

    function handleSubmit(event) {
        event.preventDefault();

        const formData = new FormData();
        formData.append("name", projectName);

        for (const [type, file] of Object.entries(files)) {
            if (file) {
                const newFileName = `${type}_${projectName}${file.name.substring(file.name.lastIndexOf("."))}`;
                formData.append(type, file, newFileName);
            }
        }

        const data = { name: projectName };
        formData.append("data", JSON.stringify(data));

        fetch(`${API_URL}/queue_render`, {
            method: "POST",
            body: formData,
        })
            .then((response) => response.json())
            .then((data) => {
                console.log("Success:", data);
                alert("Response: " + JSON.stringify(data));
                dispatch("submitSuccess");
            })
            .catch((error) => {
                console.error("Error:", error);
                alert("Error: " + error);
            });
    }

    function handleFileSelect(type, event) {
        const file = event.target.files[0];
        if (file) {
            files[type] = file;
            const reader = new FileReader();
            reader.onload = (e) => {
                document.getElementById(
                    `${type}-preview`,
                ).style.backgroundImage = `url(${e.target.result})`;
            };
            reader.readAsDataURL(file);
        }
    }
</script>

<form on:submit={handleSubmit}>
    <div class="form-group">
        <label for="name">Название папки модели:</label>
        <input type="text" id="name" bind:value={projectName} required />
    </div>

    <div class="image-inputs-container">
        <label for="image-inputs" class="image-inputs-label">IP Adapters</label>
        <div class="image-inputs">
            {#each ["front", "back", "left", "right"] as type}
                <div class="image-input">
                    <label for={type} class="file-label">
                        <div id="{type}-preview" class="file-preview">
                            <span
                                >{type.charAt(0).toUpperCase() +
                                    type.slice(1)}</span
                            >
                        </div>
                        <input
                            type="file"
                            id={type}
                            accept="image/*"
                            required
                            on:change={(e) => handleFileSelect(type, e)}
                        />
                    </label>
                </div>
            {/each}
        </div>
    </div>

    <button type="submit">Submit</button>
</form>

<style>
    form {
        display: flex;
        flex-direction: column;
        gap: 1rem;
        align-items: center;
    }

    .form-group {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.5rem;
        width: 100%;
    }

    label {
        font-weight: bold;
    }

    input[type="text"] {
        padding: 0.5rem;
        color: white;
        background-color: #2a2a2a;
        border: 1px solid #6d4567;
        border-radius: 4px;
        font-size: 1rem;
        width: 50%;
    }

    .image-inputs {
        display: grid;
        grid-template-columns: 1fr 1fr;
        grid-template-rows: 1fr 1fr;
        gap: 1rem;
        width: 300px;
        height: 300px;
    }

    .image-input {
        width: 100%;
        height: 100%;
    }

    .file-label {
        display: block;
        width: 100%;
        height: 100%;
        cursor: pointer;
    }
    .image-inputs-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.5rem;
    }

    .image-inputs-label {
        font-size: 1rem;
        color: white;
        margin-bottom: 0.5rem;
    }

    .file-preview {
        width: 100%;
        height: 100%;
        background-color: #2a2a2a;
        border: 1px solid #6d4567;
        border-radius: 4px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1rem;
        color: white;
        background-size: cover;
        background-position: center;
    }

    input[type="file"] {
        display: none;
    }

    button[type="submit"] {
        background-color: #166d3a;
        color: rgb(255, 255, 255);
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 4px;
        cursor: pointer;
        font-size: 1rem;
        transition: background-color 0.3s ease;
    }

    button[type="submit"]:hover {
        background-color: #27ae60;
    }
</style>
