<template>
  <section aria-labelledby="account-title" class="flex flex-col gap-5">
    <h1 id="account-title" class="text-lg font-semibold">{{ t('account.title') }}</h1>
    <form
      class="flex max-w-md flex-col gap-4 rounded-xl bg-white p-5 ring-1 ring-inset ring-slate-200"
      @submit.prevent="submit"
    >
      <Field input-id="ac-old" :label="t('account.oldPassword')">
        <template #default="{ inputId }">
          <TextInput
            :id="inputId"
            v-model="oldPassword"
            type="password"
            required
            autocomplete="current-password"
          />
        </template>
      </Field>
      <Field input-id="ac-new" :label="t('account.newPassword')">
        <template #default="{ inputId }">
          <TextInput
            :id="inputId"
            v-model="newPassword"
            type="password"
            required
            minlength="8"
            autocomplete="new-password"
          />
        </template>
      </Field>
      <Field input-id="ac-confirm" :label="t('account.confirm')">
        <template #default="{ inputId }">
          <TextInput
            :id="inputId"
            v-model="confirm"
            type="password"
            required
            minlength="8"
            autocomplete="new-password"
          />
        </template>
      </Field>
      <p v-if="error" role="alert" class="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
        {{ error }}
      </p>
      <p v-if="done" role="status" class="rounded-lg bg-green-50 px-3 py-2 text-sm text-green-700">
        {{ t('account.done') }}
      </p>
      <div>
        <Button type="submit" variant="primary" :loading="saving">
          {{ t('account.change') }}
        </Button>
      </div>
    </form>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Button } from '@/packages/ui/button'
import { Field } from '@/packages/ui/form'
import { TextInput } from '@/packages/ui/input'
import { changePasswordAuthPasswordPost } from '../service/generated/api'

const { t } = useI18n()
const oldPassword = ref('')
const newPassword = ref('')
const confirm = ref('')
const error = ref('')
const done = ref(false)
const pending = ref(false)
const saving = computed(() => pending.value)

async function submit() {
  error.value = ''
  done.value = false
  if (newPassword.value !== confirm.value) {
    error.value = t('account.mismatch')
    return
  }
  pending.value = true
  try {
    await changePasswordAuthPasswordPost({
      old_password: oldPassword.value,
      new_password: newPassword.value,
    })
    done.value = true
    oldPassword.value = ''
    newPassword.value = ''
    confirm.value = ''
  } catch (e) {
    error.value = String((e as { response?: { data?: { detail?: string } } }).response?.data?.detail ?? e)
  } finally {
    pending.value = false
  }
}
</script>
