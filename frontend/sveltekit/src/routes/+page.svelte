<script>
	import { API_URL } from "$lib/config.js";
	import ProjectSelector from "$lib/components/ProjectSelector.svelte";
	import RenderForm from "$lib/components/RenderForm.svelte";
	import ProgressBar from "$lib/components/ProgressBar.svelte";

	let showProgress = false;
	let progress = 0;

	function handleSubmitSuccess() {
		showProgress = true;
		startProgressPolling();
	}

	function startProgressPolling() {
		pollProgress();
	}

	function pollProgress() {
		fetch(`${API_URL}/progress`)
			.then((response) => response.json())
			.then((data) => {
				progress = data.progress;
				if (progress < 100) {
					setTimeout(pollProgress, 1000);
				}
			})
			.catch((error) => {
				console.error("Error fetching progress:", error);
			});
	}
</script>

<main>
	<h1>Animation</h1>

	<div class="card">
		<div class="header-bar">
			<h2>Project Selection</h2>
		</div>
		<div class="content">
			<ProjectSelector />
		</div>
	</div>

	<div class="card">
		<div class="header-bar">
			<h2>Render Form</h2>
		</div>
		<div class="content">
			<RenderForm on:submitSuccess={handleSubmitSuccess} />
		</div>
	</div>

	{#if showProgress}
		<div class="card">
			<div class="header-bar">
				<h2>Rendering Progress</h2>
			</div>
			<div class="content">
				<ProgressBar {progress} />
			</div>
		</div>
	{/if}
</main>

<style>
	:global(body) {
		font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
		background-color: #202020;
		color: #e0e0e0;
		line-height: 1.6;
		margin: 0;
		padding: 0;
	}

	main {
		max-width: 800px;
		margin: 2rem auto;
		padding: 0 1rem 2rem;
	}

	h1 {
		color: white;
		text-align: center;
		margin-bottom: 2rem;
	}

	.card {
		background-color: #2e2e2e;
		border-radius: 8px;
		border: 1px solid #423440;
		box-shadow: 2px 4px 6px rgba(201, 0, 201, 0.4);
		margin-bottom: 2rem;
		overflow: hidden;
	}

	.header-bar {
		background-color: #3a3a3a;
		padding: 0.75rem 1.5rem;
		border-bottom: 1px solid #423440;
	}

	h2 {
		color: white;
		margin: 0;
		font-size: 1.2rem;
	}

	.content {
		padding: 1.5rem;
	}
</style>
