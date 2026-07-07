<script setup lang="ts">
import { computed } from 'vue'
import type { AlarmItem, AlarmLevel } from '../../api/types'

const props = defineProps<{ items: AlarmItem[] }>()

const levelText: Record<AlarmLevel, string> = {
  critical: '紧急',
  major: '重要',
  minor: '次要',
  notice: '提示'
}

// Duplicate the list so the CSS marquee can loop seamlessly.
const loopItems = computed(() =>
  props.items.length ? [...props.items, ...props.items] : []
)
</script>

<template>
  <div class="alarm-scroll">
    <div class="alarm-scroll__head">
      <span class="col col--time">时间</span>
      <span class="col col--area">区域</span>
      <span class="col col--level">级别</span>
      <span class="col col--msg">告警内容</span>
    </div>
    <div class="alarm-scroll__viewport">
      <ul class="alarm-scroll__track" :style="{ animationDuration: `${items.length * 2.4}s` }">
        <li v-for="(a, i) in loopItems" :key="a.id + '-' + i" class="row">
          <span class="col col--time">{{ a.time }}</span>
          <span class="col col--area">{{ a.area }}</span>
          <span class="col col--level">
            <span class="tag" :class="`tag--${a.level}`">{{ levelText[a.level] }}</span>
          </span>
          <span class="col col--msg">{{ a.message }}</span>
        </li>
      </ul>
    </div>
  </div>
</template>

<style scoped lang="scss">
@use '../../styles/tokens' as *;

.alarm-scroll {
  height: 100%;
  display: flex;
  flex-direction: column;
  font-size: 13px;
}

.col {
  &--time {
    flex: 0 0 90px;
  }
  &--area {
    flex: 0 0 100px;
  }
  &--level {
    flex: 0 0 70px;
  }
  &--msg {
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}

.alarm-scroll__head {
  display: flex;
  padding: 4px 6px;
  color: $text-dim;
  letter-spacing: 1px;
  border-bottom: 1px solid rgba($cyan, 0.14);
}

.alarm-scroll__viewport {
  position: relative;
  flex: 1;
  overflow: hidden;
}

.alarm-scroll__track {
  list-style: none;
  animation: marquee linear infinite;
}

.alarm-scroll__viewport:hover .alarm-scroll__track {
  animation-play-state: paused;
}

.row {
  display: flex;
  align-items: center;
  padding: 7px 6px;
  border-bottom: 1px solid rgba($cyan, 0.06);
  color: $text;

  &:hover {
    background: rgba($cyan, 0.06);
  }
}

.tag {
  display: inline-block;
  padding: 1px 8px;
  border-radius: 3px;
  font-size: 12px;
  border: 1px solid currentColor;

  &--critical {
    color: $critical;
  }
  &--major {
    color: $major;
  }
  &--minor {
    color: $minor;
  }
  &--notice {
    color: $notice;
  }
}

@keyframes marquee {
  from {
    transform: translateY(0);
  }
  to {
    transform: translateY(-50%);
  }
}
</style>
