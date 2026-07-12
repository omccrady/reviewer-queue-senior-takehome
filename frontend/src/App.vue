<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import {
  applyReviewAction,
  fetchReviewItems,
  type ReviewAction,
  type ReviewItem
} from "./api";

const currentReviewer = "alex";
const items = ref<ReviewItem[]>([]);
const selectedId = ref<string | null>(null);
const isLoading = ref(false);
const errorMessage = ref<string | null>(null);
const pendingAction = ref<ReviewAction | null>(null);

const selectedItem = computed(() =>
  items.value.find((item) => item.id === selectedId.value) ?? items.value[0] ?? null
);

const availableActions = computed<ReviewAction[]>(() => {
  if (!selectedItem.value) {
    return [];
  }

  switch (selectedItem.value.status) {
    case "unassigned":
      return ["claim"];
    case "in_review":
      return ["approve", "reject", "escalate"];
    default:
      return [];
  }
});

const helperText = computed(() => {
  if (!selectedItem.value) {
    return "Select an item to see the next action.";
  }

  switch (selectedItem.value.status) {
    case "unassigned":
      return "Claim to begin review.";
    case "in_review":
      return selectedItem.value.assigned_reviewer === currentReviewer
        ? "You are already reviewing this item. Choose a decision."
        : "This item is already in review. Choose a decision.";
    case "approved":
      return "This item is already approved and no further actions are available.";
    case "rejected":
      return "This item is already rejected and no further actions are available.";
    case "escalated":
      return "This item is already escalated and no further actions are available.";
    default:
      return "No next action is available.";
  }
});

async function loadItems() {
  isLoading.value = true;
  errorMessage.value = null;

  try {
    items.value = await fetchReviewItems();
    selectedId.value = selectedItem.value?.id ?? null;
  } catch (error) {
    errorMessage.value = "Something went wrong loading the queue.";
  } finally {
    isLoading.value = false;
  }
}

async function performAction(action: ReviewAction) {
  if (!selectedItem.value) return;

  pendingAction.value = action;
  errorMessage.value = null;

  try {
    const updated = await applyReviewAction(selectedItem.value.id, action, currentReviewer);
    items.value = items.value.map((item) => (item.id === updated.id ? updated : item));
    selectedId.value = updated.id;
  } catch (error) {
    errorMessage.value = "That action could not be completed.";
  } finally {
    pendingAction.value = null;
  }
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat("en-GB", {
    dateStyle: "medium",
    timeStyle: "short"
  }).format(new Date(value));
}

function canPerform(action: ReviewAction) {
  return availableActions.value.includes(action);
}

onMounted(loadItems);
</script>

<template>
  <main class="page-shell">
    <header class="topbar">
      <div>
        <p class="eyebrow">Reviewer workspace</p>
        <h1>Active queue</h1>
      </div>
      <div class="reviewer">Signed in as {{ currentReviewer }}</div>
    </header>

    <p v-if="errorMessage" class="error-banner">{{ errorMessage }}</p>
    <p v-if="isLoading" class="loading">Loading review items...</p>

    <section v-else class="workspace">
      <aside class="queue-list" aria-label="Review queue">
        <button
          v-for="item in items"
          :key="item.id"
          class="queue-item"
          :class="{ selected: item.id === selectedItem?.id }"
          type="button"
          @click="selectedId = item.id"
        >
          <span class="queue-title">{{ item.title }}</span>
          <span class="queue-meta">{{ item.risk_level }} risk · {{ item.customer_tier }}</span>
          <span class="queue-meta">{{ item.status }} · {{ item.assigned_reviewer ?? "unassigned" }}</span>
        </button>
      </aside>

      <section v-if="selectedItem" class="detail-panel">
        <div class="detail-header">
          <div>
            <p class="eyebrow">{{ selectedItem.id }}</p>
            <h2>{{ selectedItem.title }}</h2>
          </div>
          <span class="status-pill">{{ selectedItem.status }}</span>
        </div>

        <dl class="facts">
          <div>
            <dt>Submitted</dt>
            <dd>{{ formatDate(selectedItem.submitted_at) }}</dd>
          </div>
          <div>
            <dt>Risk</dt>
            <dd>{{ selectedItem.risk_level }}</dd>
          </div>
          <div>
            <dt>Customer</dt>
            <dd>{{ selectedItem.customer_tier }}</dd>
          </div>
          <div>
            <dt>Assignee</dt>
            <dd>{{ selectedItem.assigned_reviewer ?? "None" }}</dd>
          </div>
        </dl>

        <p class="summary">{{ selectedItem.summary }}</p>
        <p class="notes">{{ selectedItem.notes_count }} notes on this item</p>
        <p class="guidance">{{ helperText }}</p>

        <div class="actions" aria-label="Workflow actions">
          <button
            type="button"
            :disabled="Boolean(pendingAction) || !canPerform('claim')"
            @click="performAction('claim')"
          >
            Claim
          </button>
          <button
            type="button"
            :disabled="Boolean(pendingAction) || !canPerform('approve')"
            @click="performAction('approve')"
          >
            Approve
          </button>
          <button
            type="button"
            :disabled="Boolean(pendingAction) || !canPerform('reject')"
            @click="performAction('reject')"
          >
            Reject
          </button>
          <button
            type="button"
            :disabled="Boolean(pendingAction) || !canPerform('escalate')"
            @click="performAction('escalate')"
          >
            Escalate
          </button>
        </div>
      </section>
    </section>
  </main>
</template>
