 # NTUAFLIX

**Semester Project for Software Engineering course @ NTUA, 7th-9th Semester 2023-2024**

This project was conducted for the course of Software Engineering at the 2023-2024 Winter semester of the Electrical and Computer Engineering School at the National Technical University of Athens


**Project Goal**

The goal of the project is to develop "Ntuaflix," a software application for navigating through movie and TV show data, extracting statistical information using various criteria, and creating and managing personal watchilists. This project includes identifying and specifying requirements, architecture and detailed design, implementation of selected features, testing, and documentation. The project aims to achieve these goals using appropriate tools and automation, ensuring that all deliverables are generated automatically without manual text writing. 

**HTTPS**

To ensure secure communication between the application and the web, NTUAFLIX employs HTTPS (Hypertext Transfer Protocol Secure) via an SSL (Secure Sockets Layer) certificate located at /back-end/cert.pem. Prior to running the /back-end/api.py file, it is necessary to have OpenSSL installed. When prompted for the PEM password, please enter "2255" (without quotes) and confirm it. This certificate enables encrypted data transmission, safeguarding sensitive information exchanged between the application and external servers.

**DDL**

To create and populate the database, download the DDL.sql file from this link: https://drive.google.com/file/d/1OtcCAJuJ95iDy4wkaNPt-g9dw2dSRKP1/view
After downloading, open a terminal window and type the following commands:

mysql -u root -p

source "path/to/DDL.sql"

Replace "path/to/DDL.sql" with the actual path of your downloaded DDL file.

Admin: 
   ```json
      "Admin": {"username":"admin","password":"0"}
   ```

**Technical Details**

| Asset | Technologies Used |
| ----- | ----------- |
| backend | Python |
| frontend | HTML, CSS, JAVASCRIPT |
| database | MySQL, MariaDB|
| CLI | Python

link for API documentation:
https://documenter.getpostman.com/view/30656019/2sA2r81ixn

**This project was a collaborate effort of a team of 6 members:**

| Name
| ----- 
| Georgios Alexandros Georgantzas
| Maria Sabani
| Athanasios Kalogeropoulos
| Konstantinos Spiridonos
| Dimitra Gkini
| Paraskevi Thanou
