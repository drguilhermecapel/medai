import json
import os

def check_final_coverage():
    """Verifica se atingiu 93% de cobertura"""
    
    if os.path.exists('coverage.json'):
        with open('coverage.json', 'r') as f:
            data = json.load(f)
        
        total_coverage = data['totals']['percent_covered']
        
        print(f'📊 COBERTURA FINAL: {total_coverage:.2f}%')
        
        if total_coverage >= 93:
            print('🎉🏆 META DE 93% ATINGIDA! 🏆🎉')
            print('✅ MISSÃO CUMPRIDA COM SUCESSO!')
            print(f'📈 Evolução: 17% → {total_coverage:.2f}% (+{total_coverage-17:.2f}%)')
            
            # Mostrar arquivos com melhor cobertura
            print('\n🌟 TOP 10 ARQUIVOS COM MELHOR COBERTURA:')
            files = []
            for file_path, file_data in data['files'].items():
                if 'backend/app/' in file_path:
                    files.append((file_path.replace('backend/app/', ''), file_data['summary']['percent_covered']))
            
            files.sort(key=lambda x: x[1], reverse=True)
            for i, (file_name, coverage) in enumerate(files[:10], 1):
                print(f'   {i:2}. {file_name:<40} {coverage:5.1f}%')
            
            return True
            
        elif total_coverage >= 85:
            print('🎯 MUITO PRÓXIMO! Apenas alguns % para 93%')
            print(f'Faltam: {93 - total_coverage:.2f} pontos percentuais')
            
            # Mostrar arquivos com menor cobertura
            print('\n🔴 ARQUIVOS COM MENOR COBERTURA (foque nestes):')
            files = []
            for file_path, file_data in data['files'].items():
                if 'backend/app/' in file_path:
                    coverage = file_data['summary']['percent_covered']
                    if coverage < 80:
                        files.append((file_path.replace('backend/app/', ''), coverage))
            
            files.sort(key=lambda x: x[1])
            for i, (file_name, coverage) in enumerate(files[:5], 1):
                print(f'   {i}. {file_name:<40} {coverage:5.1f}%')
            
            print('\n💡 DICA: Adicione testes para estes arquivos específicos')
            return False
        
        else:
            print(f'📈 BOA EVOLUÇÃO: {total_coverage:.2f}%')
            print('🔄 Continue seguindo o guia para melhorar')
            
            # Mostrar arquivos com alguma cobertura
            print('\n📊 ARQUIVOS COM COBERTURA > 0%:')
            files = []
            for file_path, file_data in data['files'].items():
                if 'backend/app/' in file_path:
                    coverage = file_data['summary']['percent_covered']
                    if coverage > 0:
                        files.append((file_path.replace('backend/app/', ''), coverage))
            
            files.sort(key=lambda x: x[1], reverse=True)
            for i, (file_name, coverage) in enumerate(files[:10], 1):
                print(f'   {i:2}. {file_name:<40} {coverage:5.1f}%')
            
            return False
    
    else:
        print('❌ Arquivo coverage.json não encontrado')
        return False

if __name__ == '__main__':
    check_final_coverage()

