import { contextBridge, ipcRenderer } from 'electron';

// Expose safe, structured APIs to the React renderer
contextBridge.exposeInMainWorld('api', {
  invoke: (channel: string, payload?: any): Promise<any> => {
    // Whitelist secure channels
    const validChannels = [
      'scenarios:list',
      'scenarios:save',
      'scenarios:saveNote',
      'scenarios:listNotes',
      'explosives:list',
      'materials:listProfiles',
      'materials:getPIEnvelopes',
      'blast:calculateEnvironment',
      'material:assessBatch',
      'research:parametricSweep',
      'research:compareScenarios',
      'units:list',
      'units:convert',
      'ufc:search',
      'validation:runSweep',
      'validation:getSummary',
      'studies:distanceSweep',
      'studies:chargeSweep',
      'studies:explosiveComparison',
      'studies:runGrid',
      'studies:exportCSV',
      'inverse:predict',
      'database:export',
      'database:import',
      'test:kill-solver',
      'test:freeze-solver',
      'test:crash-solver',
      'test:get-recovery-attempts',
      'test:reset-recovery-attempts'
    ];
    
    if (validChannels.includes(channel)) {
      return ipcRenderer.invoke(channel, payload);
    }
    
    return Promise.reject(new Error(`Security Block: IPC channel '${channel}' is not whitelisted in preload.`));
  },
  onSolverStatus: (callback: (data: any) => void) => {
    const subscription = (_event: any, value: any) => callback(value);
    ipcRenderer.on('solver:status', subscription);
    return () => {
      ipcRenderer.removeListener('solver:status', subscription);
    };
  }
});
