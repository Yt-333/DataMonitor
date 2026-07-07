<script setup lang="ts">
defineProps<{ title?: string }>()
</script>

<template>
  <section class="border-box">
    <span class="corner tl" />
    <span class="corner tr" />
    <span class="corner bl" />
    <span class="corner br" />
    <header v-if="title" class="border-box__title">
      <span class="dot" />
      <span class="label">{{ title }}</span>
    </header>
    <div class="border-box__body">
      <slot />
    </div>
  </section>
</template>

<style scoped lang="scss">
@use '../../styles/tokens' as *;

.border-box {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  border: 1px solid rgba($cyan, 0.22);
  background:
    linear-gradient(180deg, rgba($cyan, 0.05), transparent 60%), $bg-panel;
  box-shadow:
    0 0 22px rgba($nebula-blue, 0.12),
    inset 0 0 24px rgba($nebula-blue, 0.05);
  backdrop-filter: blur(2px);
}

.corner {
  position: absolute;
  width: 14px;
  height: 14px;
  border-color: $cyan;
  border-style: solid;
  border-width: 0;
  filter: drop-shadow(0 0 4px rgba($cyan, 0.8));

  &.tl {
    top: -1px;
    left: -1px;
    border-top-width: 2px;
    border-left-width: 2px;
  }
  &.tr {
    top: -1px;
    right: -1px;
    border-top-width: 2px;
    border-right-width: 2px;
  }
  &.bl {
    bottom: -1px;
    left: -1px;
    border-bottom-width: 2px;
    border-left-width: 2px;
  }
  &.br {
    bottom: -1px;
    right: -1px;
    border-bottom-width: 2px;
    border-right-width: 2px;
  }
}

.border-box__title {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  font-size: 16px;
  letter-spacing: 2px;
  border-bottom: 1px solid rgba($cyan, 0.14);

  .dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: $cyan;
    box-shadow: 0 0 8px $cyan;
  }
  .label {
    @include glow-text($text);
    font-weight: 600;
  }
}

.border-box__body {
  position: relative;
  flex: 1;
  min-height: 0;
  padding: 10px 14px;
}
</style>
