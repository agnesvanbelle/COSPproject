/*
 * Terrier - Terabyte Retriever 
 * Webpage: http://terrier.org 
 * Contact: terrier{a.}dcs.gla.ac.uk
 * University of Glasgow - School of Computing Science
 * http://www.gla.ac.uk/
 * 
 * The contents of this file are subject to the Mozilla Public License
 * Version 1.1 (the "License"); you may not use this file except in
 * compliance with the License. You may obtain a copy of the License at
 * http://www.mozilla.org/MPL/
 *
 * Software distributed under the License is distributed on an "AS IS"
 * basis, WITHOUT WARRANTY OF ANY KIND, either express or implied. See
 * the License for the specific language governing rights and limitations
 * under the License.
 *
 * The Original Code is TF_IDF.java.
 *
 * The Original Code is Copyright (C) 2004-2011 the University of Glasgow.
 * All Rights Reserved.
 *
 * Contributor(s):
 *   Ben He <ben{a.}dcs.gla.ac.uk> (original author)
 *   Gianni Amati <gba{a.}fub.it> 
 *   Vassilis Plachouras <vassilis{a.}dcs.gla.ac.uk>
 */
package org.terrier.matching.models;

import java.util.HashMap;

import org.terrier.applications.DataHolder;
import org.terrier.matching.WeightReader;
import org.terrier.structures.indexing.DocIndexToCSV;

/**
 * This class implements the TF_IDF weighting model.
 * tf is given by Robertson's tf and idf is given by the 
 * standard Sparck Jones' idf [Sparck Jones, 1972].
 * @author Ben He, Gianni Amati, Vassilis Plachouras
  */
public class TF_IDF extends WeightingModel {
	
	private static final long serialVersionUID = 1L;

	/** model name */
	private static final String name = "TF_IDF";

	/** The constant k_1.*/
	private double k_1 = 1.2d;
	
	/** The constant b.*/
	private double b = 0.75d;

	// added
	public static HashMap<Integer, String> docIDToName;		
	public static  WeightReader weightReader;
	
	public TF_IDF() {
		
		
		super();
		
		System.out.println("tf-idf constructor "   );
		
		docIDToName = DocIndexToCSV.readCsvFile(DocIndexToCSV.csvFileName);
		weightReader = new WeightReader(DataHolder.fileNameSimilarities);
		
	}
	/** 
	 * Constructs an instance of TF_IDF
	 * @param _b
	 */
	public TF_IDF(double _b) {
		this();
		this.b = _b;
	}

	/**
	 * Returns the name of the model, in this case "TF_IDF"
	 * @return the name of the model
	 */
	public final String getInfo() {
		return name;
	}
	/**
	 * Uses TF_IDF to compute a weight for a term in a document.
	 * @param tf The term frequency of the term in the document
	 * @param docLength the document's length
	 * @return the score assigned to a document with the given 
	 *		 tf and docLength, and other preset parameters
	 */
	public final double score(double tf, double docLength) {
		
		//System.out.println("Calculating tf-idf in  score(double tf, double docLength)"   );
		double weight = weightReader.get_weight(DataHolder.currentQueryTotal, DataHolder.currentQueryTerm, DataHolder.currentDocName);
		//System.out.println("Weight for " + DataHolder.currentQueryTotal + ", " + DataHolder.currentQueryTerm + ", " + DataHolder.currentDocName + ": " +
							//weight);
		
		
		double Robertson_tf = k_1*tf/(tf+k_1*(1-b+b*docLength/averageDocumentLength));
		double idf = Idf.log(numberOfDocuments/documentFrequency+1);
		
		double tf_idf =  keyFrequency * Robertson_tf * idf;
		
		
		
		double new_tf_idf = tf_idf + (weight * tf_idf);
		
		//System.out.println("tf-idf= " + tf_idf + ", weight=" + weight + ", new_tf_idf= " + new_tf_idf );
		
		//return new_tf_idf;
		
		return tf_idf;
	}
	/**
	 * Uses TF_IDF to compute a weight for a term in a document.
	 * @param tf The term frequency of the term in the document
	 * @param docLength the document's length
	 * @param documentFrequency The document frequency of the term (ignored)
	 * @param termFrequency the term frequency in the collection (ignored)
	 * @param keyFrequency the term frequency in the query (ignored).
	 * @return the score assigned by the weighting model TF_IDF.
	 */
	public final double score(
		double tf,
		double docLength,
		double documentFrequency,
		double termFrequency,
		double keyFrequency) 
	{
		System.out.println("Calculating tf-idf in score(double tf,	double docLength,	double documentFrequency,	double termFrequency,	double keyFrequency) "  );
		
		
		
		
		double Robertson_tf = k_1*tf/(tf+k_1*(1-b+b*docLength/averageDocumentLength));
		double idf = Idf.log(numberOfDocuments/documentFrequency+1);
		return keyFrequency*Robertson_tf * idf;

	}

	/**
	 * Sets the b parameter to ranking formula
	 * @param _b the b parameter value to use.
	 */
	public void setParameter(double _b) {
		this.b = _b;
	}


	/**
	 * Returns the b parameter to the ranking formula as set by setParameter()
	 */
	public double getParameter() {
		return this.b;
	}
}
