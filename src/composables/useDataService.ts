import { inject } from 'vue'
import type { DataService } from '../api/types'
import { dataServiceKey } from '../api/types'

/** Resolve the DataService provided at the app root. */
export function useDataService(): DataService {
  const service = inject<DataService>(dataServiceKey)
  if (!service) {
    throw new Error('DataService was not provided. Did you call app.provide(dataServiceKey, ...)?')
  }
  return service
}
