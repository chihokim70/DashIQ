# Infrastructure - 인프라 및 배포

## 📋 개요
Infrastructure는 AiGov 솔루션의 인프라 구성, 배포, 모니터링을 관리하는 폴더입니다.

## 🏗️ 구조
```
infrastructure/
├── kubernetes/                  # K8s 매니페스트
│   ├── deployments/             # 배포 매니페스트
│   ├── services/                # 서비스 매니페스트
│   ├── ingress/                 # 인그레스 매니페스트
│   ├── configmaps/              # 설정 맵
│   └── secrets/                 # 시크릿
├── terraform/                   # 인프라 코드
│   ├── modules/                 # Terraform 모듈
│   └── environments/            # 환경별 설정
├── ansible/                     # 배포 자동화
│   ├── playbooks/               # Ansible 플레이북
│   ├── inventory/               # 인벤토리
│   └── roles/                   # Ansible 롤
├── monitoring/                  # 프로메테우스, 그라파나 설정
│   ├── prometheus/              # Prometheus 설정
│   ├── grafana/                 # Grafana 설정
│   └── alertmanager/            # AlertManager 설정
├── scripts/                     # 배포 스크립트
│   ├── deployment/              # 배포 스크립트
│   ├── backup/                  # 백업 스크립트
│   └── maintenance/             # 유지보수 스크립트
└── README.md
```

## 🎯 주요 기능
- **Kubernetes**: 컨테이너 오케스트레이션
- **Terraform**: 인프라 코드 관리
- **Ansible**: 배포 자동화
- **모니터링**: Prometheus, Grafana 설정
- **스크립트**: 배포, 백업, 유지보수 자동화

## 🚀 시작하기
```bash
# Kubernetes 배포
kubectl apply -f kubernetes/

# Terraform 실행
terraform init
terraform plan
terraform apply

# Ansible 실행
ansible-playbook -i inventory playbooks/deploy.yml
```
