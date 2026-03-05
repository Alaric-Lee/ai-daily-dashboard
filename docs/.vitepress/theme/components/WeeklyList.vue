<template>
  <div class="weekly-list">
    <h3>周报列表</h3>
    <div v-if="items.length === 0" class="empty">
      暂无周报
    </div>
    <ul v-else>
      <li v-for="item in items" :key="item.date" class="weekly-item">
        <a :href="item.link" class="weekly-link">
          {{ item.title }}
        </a>
        <span class="weekly-date">{{ item.date }}</span>
      </li>
    </ul>
  </div>
</template>

<script setup>
defineProps({
  items: {
    type: Array,
    default: () => []
  }
})
</script>

<style scoped>
.weekly-list {
  padding: 1rem;
  background: var(--vp-code-bg);
  border-radius: var(--vp-radius);
  margin: 1rem 0;
}

.weekly-list h3 {
  margin: 0 0 1rem 0;
  font-size: 1.2rem;
  color: var(--vp-c-text-1);
}

.empty {
  color: var(--vp-c-text-3);
  text-align: center;
  padding: 2rem;
}

.weekly-item {
  margin: 0.5rem 0;
  padding: 0.5rem 0;
  border-bottom: 1px solid var(--vp-c-divider);
}

.weekly-item:last-child {
  border-bottom: none;
}

.weekly-link {
  color: var(--vp-c-brand);
  text-decoration: none;
  font-weight: 500;
  display: block;
  margin-bottom: 0.25rem;
}

.weekly-link:hover {
  text-decoration: underline;
}

.weekly-date {
  font-size: 0.85rem;
  color: var(--vp-c-text-3);
}
</style>