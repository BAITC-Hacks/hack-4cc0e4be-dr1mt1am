import { createContext, useContext } from 'react';
import type { Catalog } from './types';
import { directionNames, districtNames, districtProfiles, initiativeNames } from '../data/catalog';
import type { Direction, IndicatorId } from '../types';
export function presentCatalog(catalog: Catalog) {
  return {
    ...catalog,
    districts: catalog.districts.map(item => ({ ...item, name: districtNames[item.id] ?? item.name, profile: districtProfiles[item.id] ?? item.profile })),
    initiatives: catalog.initiatives.map(item => ({ ...item, name: initiativeNames[item.id] ?? item.name })),
    directions: (Object.keys(catalog.direction_weights) as Direction[]).map(id => ({
      id, name: directionNames[id] ?? id,
      indicators: Object.values(catalog.indicator_metadata).filter(item => item.direction === id).map(item => item.id as IndicatorId),
    })),
  };
}
export type DisplayCatalog = ReturnType<typeof presentCatalog>;
const CatalogContext = createContext<DisplayCatalog | null>(null);
export const CatalogProvider = CatalogContext.Provider;
export function useCatalog(): DisplayCatalog {
  const value = useContext(CatalogContext);
  if (!value) throw new Error('CatalogProvider is required');
  return value;
}
