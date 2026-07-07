<template>
  <div class="loading">
    <div class="ring">
      <span class="orbit" />
      <span class="orbit orbit--2" />
      <span class="core" />
    </div>
    <p class="loading__text">星云数据链路初始化…</p>
  </div>
</template>

<style scoped lang="scss">
@use '../../styles/tokens' as *;

.loading {
  position: absolute;
  inset: 0;
  z-index: 50;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 26px;
  background: rgba($bg-deep, 0.72);
  backdrop-filter: blur(4px);
}

.ring {
  position: relative;
  width: 120px;
  height: 120px;
}

.orbit {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  border: 2px solid transparent;
  border-top-color: $cyan;
  border-right-color: rgba($nebula-blue, 0.5);
  animation: spin 1.3s linear infinite;
}

.orbit--2 {
  inset: 18px;
  border-top-color: $purple;
  border-left-color: rgba($purple, 0.5);
  animation-duration: 1.9s;
  animation-direction: reverse;
}

.core {
  position: absolute;
  inset: 46px;
  border-radius: 50%;
  background: radial-gradient($cyan, $nebula-blue);
  box-shadow: 0 0 24px $cyan;
  animation: pulse 1.4s ease-in-out infinite;
}

.loading__text {
  letter-spacing: 4px;
  font-size: 15px;
  @include glow-text($text);
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
@keyframes pulse {
  0%,
  100% {
    transform: scale(0.85);
    opacity: 0.75;
  }
  50% {
    transform: scale(1.1);
    opacity: 1;
  }
}
</style>
