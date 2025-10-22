import { Shield, Zap, Lock } from 'lucide-react';

export function WelcomeScreen() {
  const features = [
    {
      icon: Shield,
      title: '보안 필터링',
      description: '모든 프롬프트는 기업 보안 정책에 따라 자동으로 필터링됩니다',
    },
    {
      icon: Zap,
      title: '다중 LLM 지원',
      description: 'GPT-4, Claude 등 다양한 LLM 모델을 선택하여 사용할 수 있습니다',
    },
    {
      icon: Lock,
      title: 'On-Premise 운영',
      description: '모든 데이터는 기업 내부 서버에서 처리되어 안전합니다',
    },
  ];

  return (
    <div className="flex flex-col items-center justify-center px-4 py-12">
      <div className="text-center mb-12">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-blue-600 to-purple-600 rounded-2xl mb-6">
          <div className="w-8 h-8 text-white font-bold text-xl flex items-center justify-center">
            AI
          </div>
        </div>
        <h1 className="text-3xl mb-3 text-gray-900">
          Enterprise LLM Proxy에 오신 것을 환영합니다
        </h1>
        <p className="text-gray-600 max-w-2xl mx-auto">
          보안이 강화된 기업용 AI 어시스턴트로 안전하게 업무 효율성을 높이세요
        </p>
      </div>

             <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl w-full mb-16">
               {features.map((feature, index) => (
                 <div
                   key={index}
                   className="bg-white rounded-xl p-6 border border-gray-200 hover:shadow-lg transition-shadow"
                 >
                   <div className="w-12 h-12 bg-blue-50 rounded-lg flex items-center justify-center mb-4">
                     <feature.icon className="w-6 h-6 text-blue-500" />
                   </div>
                   <h3 className="mb-2 text-gray-900 font-medium">{feature.title}</h3>
                   <p className="text-sm text-gray-600 leading-relaxed">{feature.description}</p>
                 </div>
               ))}
             </div>
    </div>
  );
}
