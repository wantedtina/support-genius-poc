
## Enterprise Application RCA Request: RPA Platform  

**1. Application Overview**  

*   **Purpose:** The RPA platform provides Robotic Process Automation (RPA) capabilities to Citi business users. RPA developers use the platform (Automation Anywhere) to develop and test bots. These bots automate business use cases in production across three regional environments (NAM, APAC, EMEA) for global Citi internal users. It helps automate processes and remediate end-user computing tasks.  
*   **Industry:** Financial Services (Banking)  

**2. Technical Architecture**  

*   **Architecture Type:** Automation Anywhere (vendor product) installed on Windows server. The ecosystem development components are built using microservices architecture.  
*   **Technology Stack:**  
    *   **Frontend:** Not explicitly mentioned in provided document.  
    *   **Backend:** Java using Spring Boot.  
    *   **Database:** MS SQL Server (Control Room Database and Ecosystem Database)  
    *   Automation Anywhere is the primary vendor-provided software installed in Windows Server.  
*   **Deployment:** On-premises Windows Server 2019, SQL Server 2019.  
*   **Components:**  
    *   **Control Central:** Java spring boot service, provides bot runner vdi screen stream to the RPA bot user and command to execute task in vdi (for example, reboot vdi, restart specific services, extract some log or files and send with email)  
    *   **RDP Service:** Builds RDP connection to bot runner VDI in the backend server.  
    *   **Credential Service:** Retrieves passwords from CyberArk (internal password management).  
    *   **Authentication Service:** Provides Single Sign-On (SSO) for Control Central login.  
    *   **STEData Service:** Allows applications and other services to access the database.  

**3. Data Flows and Integrations**  

*   **Data Movement:**  

    *   **Ecosystem Database**  
        *   **Purpose:** (To be defined)  
        *   **Data Stored:** (To be defined)  
        *   **Tables/Schemas:** (To be defined)  
        *   **Data Movement with Ecosystem:** (To be defined)  
    *   **Control Room Database**  
        *   **Purpose:** This database is central to the Automation Anywhere platform. It stores configuration data, bot metadata, scheduling information, user credentials, audit logs, and runtime information. *Assumption: This database is critical for managing the bots and the overall platform.*  
        *   **Data Stored:**  
            *   Bot definitions (workflows, tasks, scripts).  
            *   User accounts and roles.  
            *   Schedules for bot execution.  
            *   Runtime logs (execution status, errors, warnings).  
            *   Configuration settings for the Control Room and its components.  
            *   Credentials (encrypted) for accessing systems and applications.  
            *   Audit logs (user actions, system events).  
        *   **Tables/Schemas:** It's difficult to know the exact table structure without direct access, but you could expect tables related to:  
            *   Bots  
            *   Users  
            *   Schedules  
            *   Devices (Bot Runners)  
            *   Credentials  
            *   Logs  
            *   Settings  
        *   **Data Movement with Automation Anywhere:**  
            *   **Bot Development:**  
                *   Developers create bots within the Automation Anywhere development environment (part of the Control Room).  
                *   Bot definitions and metadata are stored in the Control Room Database.  
            *   **Bot Deployment & Scheduling:**  
                *   Bots are deployed to Bot Runners (devices that execute the bots).  
                *   Scheduling information is stored in the Control Room Database.  
                *   At runtime, the Control Room instructs Bot Runners to execute specific bots based on the schedule.  
            *   **Bot Execution:**  
                *   Bot Runners retrieve bot definitions and credentials from the Control Room Database.  
                *   Bots interact with various systems (applications, databases, APIs) to automate tasks.  
            *   **Data Interaction during Bot Execution:**  
                *   Bots read data from and write data to applications, databases, and files.  
                *   *Assumption: If a bot needs to retrieve a password, it interacts with the Credential Service, which fetches the password from CyberArk.*  
                *   *Assumption: Bots may use the STEData Service to read from or write to the Ecosystem Database.*  
            *   **Logging and Monitoring:**  
                *   Bot Runners send execution logs (status, errors, warnings) back to the Control Room.  
                *   The Control Room stores these logs in the Control Room Database.  
                *   Monitoring dashboards display data retrieved from the Control Room Database.  
*   **Data Flow Diagram:** (To be provided)  

*   **External Integrations:** (Needs more detailed explanation - Request clarification) Detail any third-party APIs or services used. Specifically, mention integrations with Office Suite, ERP, CRM, and legacy systems.  

**4. User Roles and Permissions**  

*   **User Roles:** Developers, Testers, Business Users.  
*   **Permissions:**  
    *   Role-based access control for bot creation, modification, and execution.  
    *   Access levels are based on the principle of least privilege.  
    *   Credential Management: Secure storage and management of credentials.  

**5. Monitoring and Logging**  

*   **Tools:** ITRS Samler, and ITRStrigger Powershell Script to monitor Server and VDI  
*   **Logs:** Control Room Logs stored in Application server, Ecosystem Log stored in application server, bot runner log and vdi log stored in VDIs  

**6. (Intentionally Skipped)**  

**7. (Intentionally Skipped)**  

**8. Infrastructure**  

*   **Setup:**  
    *   3 Windows servers as application servers build cluster node for control room  
    *   2 windows server as application servers build cluster for ecosystem application  
    *   2 MS SQL databases adopt always on configuration,  
    *   and network configurations adopt Citi internal network configuration.  
*   **Capacity:**  
    *   Application servers: 32 GB Memory, 8 CPU  

**9. Security Configurations**  

*   **Measures:**  
    *   **Control Room Access:** Role-based access control. Activity Directory Password for user login  
    *   **Control Central Access:** Role-based access control, inherit from control room roles. Signal Sign On for user login  

**10. Business Processes**  

*   **Interaction with Control Room**  
    *   **User login:** User login Control Room with enterprise AD password  
    *   **Bot Development and Testing**  
        *   **Bot Creation:** Use bot creator tool to develop bot  
        *   **Bot Export & Import:** Export & Import developed bot to package from Dev for promotion to UAT or Production  
        *   **Bot Scheduling:** Through the Control Room, Emily schedules the bot to run every morning at 7:00 AM to process onboarding tasks received the previous day.  
*   **Interaction with Control Central:** Control Central provides a secure and centralized platform for authorized users (e.g., RPA Admins, IT Analysts) to log in and manage Bot Runner VDIs.  
    *   **Process:**  
        *   The user accesses the Control Central interface via a web browser or designated client software.  
        *   The user logs in using corporate credentials, which are verified through the Single Sign-On (SSO) feature provided by the Authentication Service.  
        *   User is able to perform below task in Control Central  
            *   View Bot Runner VDI to monitor the ongoing running bot  
            *   Send Command to VDI for maintenance  
                *   Reboot VDI  
                *   Restart bot runner agent  
                *   Export log  

**11. Known Issues and History**  

*   **Past Problems:** (To be filled when an incident occurs) Mention any similar historical issues.  
*   **Third-Party Components:** Note the status and versions of external components, specifically Automation Anywhere.  

**12. Testing Environments**  

*   **Test Cases:** (To be filled when an incident occurs) Indicate if the issue appears in testing.  
*   **Test Coverage:** (To be filled when an incident occurs) Assess the quality of test coverage. Bots are rigorously tested in the UAT environment.  

**13. RCA and Solution Instructions**  

*   **Root Cause:** (To be filled during RCA) Request detailed analysis.  
*   **Solutions:** (To be filled during RCA) Prioritized actions, workarounds, tools.  
*   **Risks:** (To be filled during RCA) Assess implementation risks.  
*   **Experts:** (To be filled during RCA) Advise on specialist involvement.  
*   **Additional Data:** (To be filled during RCA) Request if more info needed.  

This structure provides a template for documenting future incidents and performing RCAs. Remember to fill in the sections related to specific problems and incidents as they occur. The sections marked "(Needs more detailed explanation - Request clarification)" need more information to be useful for RCA.
