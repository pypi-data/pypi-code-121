from string import Template

"""Unused"""
ComponentTemplate = Template(
r"""<template>
</template>

<script setup lang="ts">
import {
  toRefs
} from 'vue'

import { useStore } from 'vuex'
import { useModule } from '@savitri/frontend'

const store = useStore()
const moduleRefs = reactive(useModule('${name}', store))

const {
  item,
  items

} = toRefs(moduleRefs)
</script>
""")

InternalHomeComponentTemplate = Template(
r"""<template>
  <sv-prose class="mt-4">
    <template #title>Parabéns</template>
    <ul class="flex flex-col gap-y-3 list-disc pl-4">
      <li
        v-for="(item, index) in items"
        v-html="item"
        :key="`item-$${index}`"
      />
    </ul>
  </sv-prose>
</template>

<script setup lang="ts">
import { inject } from 'vue'
import { SvProse } from '@savitri/components'

const productName = inject('productName')
const baseVersion = inject('baseVersion')

const items = [
  'Você configurou um projeto com sucesso',
  'Nome do projeto : ' + productName,
  'Versão do Savitri: ' + baseVersion
]
</script>
""")
