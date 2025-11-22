/**
 * Pet State Models - TypeScript/ArkTS
 * Auto-generated from contracts/pet_state.json
 */

export type PetMood =
  | 'Happy'
  | 'Energetic'
  | 'Sleepy'
  | 'Concerned'
  | 'Anxious'
  | 'Recovering'
  | 'Proud';

export type Animation =
  | 'smile'
  | 'jump'
  | 'sleep'
  | 'worry'
  | 'celebrate'
  | 'breathe';

export type HapticPattern =
  | 'gentle'
  | 'alert'
  | 'celebration'
  | 'warning';

/**
 * Pet state update from Cloud to Phone/Watch
 */
export interface PetState {
  mood: PetMood;
  energy: number;  // 0-100 percentage
  timestamp: number;
  message?: string;
  animation?: Animation;
  hapticPattern?: HapticPattern;
  imageUrl?: string;
}

/**
 * Validate pet state against schema
 */
export function validatePetState(state: any): state is PetState {
  if (!state.mood || typeof state.mood !== 'string') {
    return false;
  }
  if (typeof state.energy !== 'number' || state.energy < 0 || state.energy > 100) {
    return false;
  }
  if (typeof state.timestamp !== 'number') {
    return false;
  }
  return true;
}
