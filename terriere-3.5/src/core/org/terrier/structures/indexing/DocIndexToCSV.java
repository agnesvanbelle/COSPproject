package org.terrier.structures.indexing;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.HashMap;

public class DocIndexToCSV {

	/**
	 * @param args
	 */

	public static final String csvFileName = "docIdToName.csv";

	public static void main(String[] args) {
		// generateCsvFile("docIDToName.csv");

	}

	public static void writeToCsvFile(String sFileName, Integer docId, String docName) {
		try {
			FileWriter writer = new FileWriter(sFileName, true);

			writer.append(docId.toString());
			writer.append(',');
			writer.append(docName);
			writer.append('\n');

			writer.flush();
			writer.close();
		} catch (IOException e) {
			System.err.println("IO Exception occurred in DocIndexToCSV");
			e.printStackTrace();
		}
	}

	

	public static HashMap<Integer, String> readCsvFile(String sFileName) {

		HashMap<Integer, String> docIdToName = new HashMap<Integer, String>();

		BufferedReader br = null;
		String line = "";
		String cvsSplitBy = ",";

		try {

			br = new BufferedReader(new FileReader(sFileName));
			while ((line = br.readLine()) != null) {

				// use comma as separator
				String[] values = line.split(cvsSplitBy);
				put_values_in_hash(docIdToName, values);

			}

		} catch (FileNotFoundException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		} finally {
			if (br != null) {
				try {
					br.close();
				} catch (IOException e) {
					e.printStackTrace();
				}
			}
		}

		return docIdToName;

	}

	private static void put_values_in_hash(HashMap<Integer, String> docIdToName, String[] values) {
		Integer id = Integer.parseInt(values[0].trim());
		String name = values[1].trim();

		docIdToName.put(id, name);
		
		
		//System.out.println("Put " + id + " and " + name + " in hash for docId->Name");
	}

}
