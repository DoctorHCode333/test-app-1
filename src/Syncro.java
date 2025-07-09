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

<!-- Required by Apache POI for logging -->
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
