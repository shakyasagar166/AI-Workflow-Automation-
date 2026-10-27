import React, { useState } from 'react';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import Workflows from './pages/Workflows';
import CreateWorkflow from './pages/CreateWorkflow';
import WorkflowDetails from './pages/WorkflowDetails';

export default function App() {
  const [currentTab, setCurrentTab] = useState('dashboard');
  const [selectedWorkflowId, setSelectedWorkflowId] = useState(null);
  const [selectedExecutionId, setSelectedExecutionId] = useState(null);

  const handleSelectWorkflow = (wfId) => {
    setSelectedWorkflowId(wfId);
    setSelectedExecutionId(null);
    setCurrentTab('workflow_details');
  };

  const handleSelectExecution = (execId) => {
    setSelectedExecutionId(execId);
    setCurrentTab('workflow_details');
  };

  const handleNavigate = (tab) => {
    setCurrentTab(tab);
    if (tab !== 'workflow_details') {
      setSelectedExecutionId(null);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-blue-600 selection:text-white">
      <Navbar currentTab={currentTab} onNavigate={handleNavigate} />

      <main className="flex-1 px-4 sm:px-6 lg:px-8 pt-6">
        {currentTab === 'dashboard' && (
          <Dashboard
            onNavigate={handleNavigate}
            onSelectWorkflow={handleSelectWorkflow}
            onSelectExecution={handleSelectExecution}
          />
        )}

        {currentTab === 'workflows' && (
          <Workflows
            onNavigate={handleNavigate}
            onSelectWorkflow={handleSelectWorkflow}
            onSelectExecution={handleSelectExecution}
          />
        )}

        {currentTab === 'create' && (
          <CreateWorkflow
            onNavigate={handleNavigate}
            onSelectWorkflow={handleSelectWorkflow}
            onSelectExecution={handleSelectExecution}
          />
        )}

        {currentTab === 'workflow_details' && (
          <WorkflowDetails
            workflowId={selectedWorkflowId}
            selectedExecutionId={selectedExecutionId}
            onNavigate={handleNavigate}
            onSelectExecution={handleSelectExecution}
          />
        )}
      </main>

      <footer className="border-t border-slate-900 bg-slate-950/80 py-4 text-center text-xs text-slate-600 font-mono">
        Autonomous AI Workflow Automation System &bull; Version 1.0.0
      </footer>
    </div>
  );
}
