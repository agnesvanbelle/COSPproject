package org.terrier.matching;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.Hashtable;

import org.terrier.applications.DataHolder;

public class WeightReader {

	String file_location;
	Hashtable<String, Hashtable<String, Hashtable<String, Double>>> similarities;

	public static void main(String[] args) {

		String file = "bhat_coeffs.csv";
		WeightReader wr = new WeightReader(file);

		wr.print_hash();
		wr.get_weight("hoi kameel", "kameel", "2");

	}
	
	

	public WeightReader(String file_location) {
		this.file_location = file_location;
		similarities = new Hashtable<String, Hashtable<String, Hashtable<String, Double>>>();
		read_weights();

		if (checkFile(file_location)) {
			System.out.println("File with similarities existed");
		} else {
			System.out.println("File with similarities not found!");
		}
	}

	public boolean checkFile(String fileName) {
		File f = new File(fileName);

		return f.exists();

	}

	public double get_weight(String raw_query, String query_term, String doc_id) {
		//System.out.println("similarities.get("+raw_query+").get("+query_term+").get("+doc_id+")");
		
		if (similarities.containsKey(raw_query)) {
			if (similarities.get(raw_query).containsKey(query_term)) {
				if (similarities.get(raw_query).get(query_term).containsKey(doc_id)) {
					return similarities.get(raw_query).get(query_term).get(doc_id);
				}
			}
		}
		
		// if one of the keys isn't there, print this to error log
		try {
		    PrintWriter out = new PrintWriter(new BufferedWriter(new FileWriter(DataHolder.errorLogFileName, true)));
		    out.println("similarities.get("+raw_query+").get("+query_term+").get("+doc_id+") FAILED");
		    out.close();
		} catch (IOException e) {
		    e.printStackTrace();
		}
		
		return 0;
	}

	public void read_weights() {

		BufferedReader br = null;
		String line = "";
		String cvsSplitBy = ", ";

		try {

			br = new BufferedReader(new FileReader(file_location));
			while ((line = br.readLine()) != null) {

				// use comma as separator
				String[] values = line.split(cvsSplitBy);
				put_values_in_hash(values);

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

		System.out.println("Done reading weights.");
	}

	private void put_values_in_hash(String[] values) {
		String raw_query = values[0];
		String query_term = values[1];
		String doc_id = values[2];
		Double sim = Double.parseDouble(values[3]);
		if (similarities.containsKey(raw_query)) {

			if (similarities.get(raw_query).containsKey(query_term)) {
				if (similarities.get(raw_query).get(query_term).containsKey(doc_id)) {
					System.out.println("There are two the same key values which should not be the case");
				} else {
					similarities.get(raw_query).get(query_term).put(doc_id, sim);
				}
			} else {
				similarities.get(raw_query).put(query_term, new Hashtable<String, Double>());
				similarities.get(raw_query).get(query_term).put(doc_id, sim);
			}
		} else {
			similarities.put(raw_query, new Hashtable<String, Hashtable<String, Double>>());
			similarities.get(raw_query).put(query_term, new Hashtable<String, Double>());
			similarities.get(raw_query).get(query_term).put(doc_id, sim);
		}

	}

	public void print_hash() {
		for (String q : similarities.keySet()) {
			for (String qt : similarities.get(q).keySet()) {
				for (String d : similarities.get(q).get(qt).keySet()) {
					Double sim = similarities.get(q).get(qt).get(d);
					System.out.println(q + "-" + qt + "-" + d + "-" + sim);
				}
			}
		}
	}

}
