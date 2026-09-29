from app.services.ai_core_service import AICoreService


def main():
    service = AICoreService()

    deployment = service.get_deployment()

    print("\n========== AI CORE DEPLOYMENT ==========")

    print("Deployment ID:")
    print(service.deployment_id)

    print("\nDeployment URL:")
    print(deployment.get("deploymentUrl"))

    print("\nDeployment details:")
    print(deployment)


if __name__ == "__main__":
    main()