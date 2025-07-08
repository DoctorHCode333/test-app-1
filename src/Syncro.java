import org.apache.poi.ss.usermodel.*;
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
