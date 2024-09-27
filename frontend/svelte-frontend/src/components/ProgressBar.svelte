<script>
  export let progress = 0;
</script>

<div class="progress-container">
  <div class="progress-bar">
    <div class="progress-bar-fill" style="width: {progress}%;">
      <span class="progress-text">{progress}%</span>
    </div>
  </div>
</div>

<style>
  .progress-container {
    margin-top: 1rem;
  }

  .progress-bar {
    width: 100%;
    background-color: #e0e0e0;
    border-radius: 10px;
    overflow: hidden;
    box-shadow: inset 0 1px 3px rgba(0, 0, 0, .2);
  }

  .progress-bar-fill {
    height: 30px;
    background-color: #3498db;
    transition: width 0.5s ease-in-out;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .progress-text {
    color: white;
    font-weight: bold;
    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
  }
</style>