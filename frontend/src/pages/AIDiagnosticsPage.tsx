
import React from 'react';
import { Brain, Activity, Zap } from 'lucide-react';

const AIDiagnosticsPage = (): React.ReactElement => {
  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 flex items-center">
            <Brain className="w-8 h-8 mr-3 text-purple-600" />
            IA Diagnóstica
          </h1>
          <p className="text-gray-600 mt-2">
            Diagnósticos assistidos por inteligência artificial
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center">
              <Brain className="w-8 h-8 text-purple-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Análises Realizadas</p>
                <p className="text-2xl font-bold text-gray-900">156</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center">
              <Activity className="w-8 h-8 text-green-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Precisão Média</p>
                <p className="text-2xl font-bold text-gray-900">94.2%</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center">
              <Zap className="w-8 h-8 text-yellow-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Tempo Médio</p>
                <p className="text-2xl font-bold text-gray-900">2.3s</p>
              </div>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Sistema de IA Diagnóstica
          </h2>
          <p className="text-gray-600 mb-4">
            Nossa inteligência artificial analisa dados médicos para fornecer sugestões 
            diagnósticas precisas e rápidas, auxiliando profissionais de saúde na tomada de decisões.
          </p>
          <div className="text-center py-8">
            <Brain className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-600">
              Funcionalidade em desenvolvimento - Sistema de IA avançado para diagnósticos médicos
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIDiagnosticsPage;
