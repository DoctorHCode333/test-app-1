Aimport org.apache.poi.ss.usermodel.*;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;

import java.io.FileOutputStream;
import java.io.IOException;

public class ExcelSimpleWriter {

    public static void main(String[] args) {
        Workbook workbook = new XSSFWorkbook(); // .xlsx
        Sheet sheet = workbook.createSheet("MyData");

        // Header row
        Row header = sheet.createRow(0);
        header.createCell(0).setCellValue("ID");
        header.createCell(1).setCellValue("Name");
        header.createCell(2).setCellValue("Email");

        // Row 1
        Row row1 = sheet.createRow(1);
        row1.createCell(0).setCellValue(1);
        row1.createCell(1).setCellValue("Alice");
        row1.createCell(2).setCellValue("alice@example.com");

        // Row 2
        Row row2 = sheet.createRow(2);
        row2.createCell(0).setCellValue(2);
        row2.createCell(1).setCellValue("Bob");
        row2.createCell(2).setCellValue("bob@example.com");

        // Autosize columns
        for (int i = 0; i < 3; i++) {
            sheet.autoSizeColumn(i);
        }

        // Write the file
        try (FileOutputStream fileOut = new FileOutputStream("my-excel-file.xlsx")) {
            workbook.write(fileOut);
            workbook.close();
            System.out.println("Excel file 'my-excel-file.xlsx' created successfully.");
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}





import org.apache.poi.ss.usermodel.*;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;

import java.io.FileOutputStream;
import java.io.IOException;

public class ExcelWriter {
    public static void main(String[] args) {
        // Create a workbook
        Workbook workbook = new XSSFWorkbook();

        // Create a sheet
        Sheet sheet = workbook.createSheet("Data");

        // Sample column headers
        String[] headers = { "ID", "Name", "Email", "Age" };

        // Sample data
        String[][] data = {
            { "1", "Alice", "alice@example.com", "30" },
            { "2", "Bob", "bob@example.com", "28" },
            { "3", "Charlie", "charlie@example.com", "35" }
        };

        // Create header row
        Row headerRow = sheet.createRow(0);
        for (int i = 0; i < headers.length; i++) {
            Cell cell = headerRow.createCell(i);
            cell.setCellValue(headers[i]);
        }

        // Fill data rows
        for (int i = 0; i < data.length; i++) {
            Row row = sheet.createRow(i + 1); // Row 1 onwards
            for (int j = 0; j < data[i].length; j++) {
                row.createCell(j).setCellValue(data[i][j]);
            }
        }

        // Autosize columns
        for (int i = 0; i < headers.length; i++) {
            sheet.autoSizeColumn(i);
        }

        // Write to file
        try (FileOutputStream fileOut = new FileOutputStream("output.xlsx")) {
            workbook.write(fileOut);
            workbook.close();
            System.out.println("Excel file created successfully.");
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}

<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
  <modelVersion>4.0.0</modelVersion>

  <groupId>longtime</groupId>
  <artifactId>automation</artifactId>
  <version>0.0.1-SNAPSHOT</version>
  <packaging>jar</packaging>

  <name>automation</name>
  <url>http://maven.apache.org</url>

  <properties>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    <maven.compiler.source>1.8</maven.compiler.source>
        <maven.compiler.target>1.8</maven.compiler.target>
        <maven.shade.plugin.version>3.2.1</maven.shade.plugin.version>
        <maven.compiler.plugin.version>3.6.1</maven.compiler.plugin.version>
        <exec-maven-plugin.version>1.6.0</exec-maven-plugin.version>
        <aws.java.sdk.version>2.18.16</aws.java.sdk.version>
        <slf4j.version>1.7.28</slf4j.version>
        <junit5.version>5.8.1</junit5.version>
  </properties>

  <dependencies>
    <dependency>
      <groupId>junit</groupId>
      <artifactId>junit</artifactId>
      <version>3.8.1</version>
      <scope>test</scope>
    </dependency>
    
    <dependency>
    <groupId>com.opencsv</groupId>
    <artifactId>opencsv</artifactId>
    <version>4.1</version>
</dependency>

<dependency>
    <groupId>javax.mail</groupId>
    <artifactId>mail</artifactId>
    <version>1.5.0-b01</version>
</dependency>
        <dependency>
            <groupId>org.slf4j</groupId>
            <artifactId>slf4j-api</artifactId>
            <version>${slf4j.version}</version>
        </dependency>
		<!-- https://mvnrepository.com/artifact/com.mysql/mysql-connector-j -->
<dependency>
    <groupId>com.mysql</groupId>
    <artifactId>mysql-connector-j</artifactId>
    <version>8.3.0</version>
</dependency>
		
         <!--<dependency>
            <groupId>org.slf4j</groupId>
            <artifactId>slf4j-simple</artifactId>
            <version>${slf4j.version}</version>
        </dependency>-->

        <!-- Needed to adapt Apache Commons Logging used by Apache HTTP Client to Slf4j to avoid
        ClassNotFoundException: org.apache.commons.logging.impl.LogFactoryImpl during runtime -->
        <dependency>
            <groupId>org.apache.logging.log4j</groupId>
            <artifactId>log4j-slf4j-impl</artifactId>
            <version>2.17.2</version>
        </dependency>

        <!-- Test Dependencies -->
        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter</artifactId>
            <version>${junit5.version}</version>
            <scope>test</scope>
        </dependency>

  <!-- https://mvnrepository.com/artifact/com.mypurecloud/platform-client-v2 -->
<dependency>
    <groupId>com.mypurecloud</groupId>
    <artifactId>platform-client-v2</artifactId>
    <version>171.0.0</version>
</dependency>
  
  <dependency>
        <groupId>org.seleniumhq.selenium</groupId>
        <artifactId>selenium-java</artifactId>
        <version>3.141.59</version>
    </dependency>
    
    <dependency>
    <groupId>commons-io</groupId>
    <artifactId>commons-io</artifactId>
    <version>2.11.0</version>
</dependency>
    
    <!-- https://mvnrepository.com/artifact/com.datastax.cassandra/cassandra-driver-core -->
<dependency>
    <groupId>com.datastax.cassandra</groupId>
    <artifactId>cassandra-driver-core</artifactId>
    <version>3.10.1</version>
</dependency>
    
<!-- https://mvnrepository.com/artifact/org.json/json -->
<dependency>
    <groupId>org.json</groupId>
    <artifactId>json</artifactId>
    <version>20220924</version>
</dependency>

  
	
    
    <dependency>
      <groupId>junit</groupId>
      <artifactId>junit</artifactId>
      <version>3.8.1</version>
      <scope>test</scope>
    </dependency>
    <dependency>
    <groupId>com.amazonaws</groupId>
    <artifactId>aws-java-sdk</artifactId>
    <version>1.11.163</version>
</dependency>
 
 	


<dependency>
		<groupId>com.oracle</groupId>
		<artifactId>ojdbc</artifactId>
		<version>12.2.0.1</version>
		<scope>system</scope>
		<systemPath>C:\Harsh_official\Batch_Files\All_batch_Jobs\AutomationCopyHarsh - Copy\ojdbc7.jar</systemPath>
</dependency>
	
<dependency>
		<groupId>org.apache.httpcomponents.client5</groupId>
		<artifactId>httpclient5</artifactId>
		<version>5.1</version>
</dependency>

 
<dependency>
    <groupId>com.microsoft.sqlserver</groupId>
    <artifactId>mssql-jdbc</artifactId>
    <version>6.1.0.jre8</version>
</dependency>
   
 <dependency>
   <groupId>com.jcraft</groupId>
   <artifactId>jsch</artifactId>
   <version>0.1.42</version>
</dependency>

 <dependency>
   <groupId>org.apache.poi</groupId>
   <artifactId>poi-ooxml</artifactId>
   <version>5.2.5</version>
</dependency>
<dependency>
    <groupId>org.apache.logging.log4j</groupId>
    <artifactId>log4j-api</artifactId>
    <version>2.17.2</version>
</dependency>
<dependency>
    <groupId>org.apache.logging.log4j</groupId>
    <artifactId>log4j-core</artifactId>
    <version>2.17.2</version>
</dependency>

  </dependencies>
  <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>${maven.compiler.plugin.version}</version>
            </plugin>
        </plugins>
    </build>
</project>


    Exception in thread "main" java.lang.NoSuchMethodError: 'org.apache.commons.io.output.UnsynchronizedByteArrayOutputStream$Builder org.apache.commons.io.output.UnsynchronizedByteArrayOutputStream.builder()'
	at org.apache.poi.xssf.usermodel.XSSFWorkbook.newPackage(XSSFWorkbook.java:544)
	at org.apache.poi.xssf.usermodel.XSSFWorkbook.<init>(XSSFWorkbook.java:231)
	at org.apache.poi.xssf.usermodel.XSSFWorkbook.<init>(XSSFWorkbook.java:227)
	at org.apache.poi.xssf.usermodel.XSSFWorkbook.<init>(XSSFWorkbook.java:215)
	at longtime.automation.BulkMessageTranscriptBatchJob.main(BulkMessageTranscriptBatchJob.java:220) 

Workbook workbook = new XSSFWorkbook(); 
