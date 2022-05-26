from string import Template

RouterTemplate = Template(r"""
import { RouterExtension } from 'frontend/router'

export const routerExtension: RouterExtension = {
  //
}
""")

StoreTemplate = Template(r"""
import { StoreExtension } from 'frontend/store'

export const storeExtension: StoreExtension = {
  //
}
""")

InternalRouterTemplate = Template(r"""
import { RouterExtension } from '@savitri/frontend'

export const routerExtension: RouterExtension = {
  'dashboard': [
    {
      name: 'dashboard-home',
      path: 'home',
      component: () => import('./components/dashboard/c-home/c-home.vue'),
      meta: { title: 'Início' }
    }
  ]
}
""")
