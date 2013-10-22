package org.terrier.applications;

import java.io.File;

public class DataHolder {

	/**
	 * @param args
	 */
	public static void main(String[] args) {
		// TODO Auto-generated method stub

	}
	
	public static String fileNameSimilarities = "similarities.csv";

	public static String currentQueryTotal = "";
	
	public static String currentQueryTerm = "";
	
	public static Integer currentDocID = -1;
	
	public static String currentDocName = "";
	
	public static String errorLogFileName = "errorlog.txt";
	
	public static void removeFile(String sFileName) {
		File file = new File(sFileName);

		if (file.delete()) {
			System.out.println(file.getName() + " is deleted!");
		} else {
			System.out.println("Delete operation for " + sFileName + " in DataHolder failed.");
		}
	}
}
