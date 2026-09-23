export type DistrictId = 'Esil' | 'Almaty' | 'Saryarka' | 'Baikonur' | 'Nura';
export type Direction = 'Transport' | 'Ecology' | 'Social' | 'Safety' | 'Services';
export type IndicatorId = 'T1' | 'T2' | 'E1' | 'E2' | 'S1' | 'S2' | 'B1' | 'B2' | 'C1' | 'C2';
export type InitiativeId = `M${1|2|3|4|5|6|7|8|9|10|11|12|13|14}`;
export interface District { id: DistrictId; name: string; populationShare: number; score: number; indicators: Record<IndicatorId, number>; profile: string }
export interface Initiative { id: InitiativeId; direction: Direction; name: string; type: 'District' | 'City'; cost: number; lag: number; effects: [IndicatorId, number][]; image?: string }
export interface Decision { initiative_id: InitiativeId; district: DistrictId | null }
