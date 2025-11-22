/**
 * Pet State Machine - Core logic for pet behavior
 * Manages mood transitions based on health metrics
 */

export class PetStateMachine {
  private currentMood: PetMood = 'Happy';
  private moodChangeCallback?: (mood: PetMood) => void;

  /**
   * Update pet state based on heart rate
   * @param heartRate Current heart rate
   */
  updateFromHeartRate(heartRate: number): void {
    let newMood = this.currentMood;

    // Simple mood logic (expand based on requirements)
    if (heartRate > 180) {
      newMood = 'Concerned';
    } else if (heartRate > 140) {
      newMood = 'Energetic';
    } else if (heartRate < 50) {
      newMood = 'Sleepy';
    } else {
      newMood = 'Happy';
    }

    if (newMood !== this.currentMood) {
      this.transitionMood(newMood);
    }
  }

  /**
   * Transition to new mood state
   * @param newMood Target mood
   */
  private transitionMood(newMood: PetMood): void {
    console.info(`PetStateMachine: ${this.currentMood} -> ${newMood}`);
    this.currentMood = newMood;

    if (this.moodChangeCallback) {
      this.moodChangeCallback(newMood);
    }
  }

  /**
   * Subscribe to mood changes
   * @param callback Function to call when mood changes
   */
  onMoodChange(callback: (mood: PetMood) => void): void {
    this.moodChangeCallback = callback;
  }

  /**
   * Get current pet mood
   */
  getCurrentMood(): PetMood {
    return this.currentMood;
  }
}

export type PetMood = 'Happy' | 'Energetic' | 'Sleepy' | 'Concerned' | 'Anxious' | 'Recovering';
