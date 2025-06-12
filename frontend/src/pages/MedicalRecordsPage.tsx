
import React from 'react';
import { FileText, Search, Plus } from 'lucide-react';

const MedicalRecordsPage = (): React.ReactElement => {
  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 flex items-center">
            <FileText className="w-8 h-8 mr-3 text-green-600" />
            Prontuários Médicos
          </h1>
          <p className="text-gray-600 mt-2">
            Gestão de prontuários eletrônicos
          </p>
        </div>
        
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex justify-between items-center mb-6">
            <div className="flex items-center space-x-4">
              <div className="relative">
                <Search className="w-5 h-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  placeholder="Buscar prontuários..."
                  className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                />
              </div>
            </div>
            <button className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors flex items-center">
              <Plus className="w-4 h-4 mr-2" />
              Novo Prontuário
            </button>
          </div>
          
          <div className="text-center py-12">
            <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Sistema de Prontuários
            </h3>
            <p className="text-gray-600">
              Funcionalidade em desenvolvimento para gestão completa de prontuários médicos
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MedicalRecordsPage;
