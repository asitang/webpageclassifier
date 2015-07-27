/*
 * Licensed to the Apache Software Foundation (ASF) under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * The ASF licenses this file to You under the Apache License, Version 2.0
 * (the "License"); you may not use this file except in compliance with
 * the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

/*
 * @author  Asitang Mishra [JPL MEMEX]
 * */




import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;

import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;

public class Categorizer {

	public static ArrayList<String> readGolden(String path) throws IOException {

		ArrayList<String> list = new ArrayList<String>();

		FileReader fileReader = new FileReader(path);

		// Always wrap FileReader in BufferedReader.
		BufferedReader bufferedReader = new BufferedReader(fileReader);
		String line = "";

		while ((line = bufferedReader.readLine()) != null) {
			// System.out.println(line);
			list.add(line);

		}
		bufferedReader.close();
		fileReader.close();

		return list;

	}

	public static ArrayList<String> nGrams(String input, int n) {

		ArrayList<String> grams = new ArrayList<String>();

		String[] parts = input.split(" ");
		for (int i = 0; i < parts.length - n + 1; i++) {
			StringBuilder sb = new StringBuilder();
			for (int k = 0; k < n; k++) {
				if (k > 0)
					sb.append(' ');
				sb.append(parts[i + k]);
			}
			grams.add(sb.toString());
		}
		return grams;

	}

	public static boolean checkforwordinurl(String url,
			ArrayList<String> wordlist) {

		for (String word : wordlist) {
			if (url.contains(word))
				return true;
		}
		return false;

	}

	public static ArrayList<String> extractallclassnames(
			ArrayList<String> taglist, String attrib, Document html_doc) {

		ArrayList<String> list = new ArrayList<String>();

		for (String tagname : taglist) {

			Elements tags = html_doc.getElementsByTag(tagname);
			for (Element tag : tags) {
				if (tag.hasAttr(attrib))
					list.add(tag.attr(attrib).toString());
			}

		}

		return list;

	}

	public static ArrayList<String> extractallfromtag(
			ArrayList<String> taglist, Document html_doc) {

		ArrayList<String> list = new ArrayList<String>();

		for (String tagname : taglist) {
			Elements tags = html_doc.getElementsByTag(tagname);
			for (Element tag : tags) {
				list.add(tag.toString());
			}
		}

		return list;

	}

	public static double cosinesimilaritymeasure(ArrayList<String> words,
			ArrayList<String> goldwords) {

		HashMap<String, Integer> wordfreq = new HashMap<String, Integer>();
		HashMap<String, Integer> goldwordfreq = new HashMap<String, Integer>();
		ArrayList<String> commonwords = new ArrayList<String>();

		double cosinesum = 0;
		double sumgoldwords = 0;
		double sumwords = 0;

		for (String word : words) {
			if (wordfreq.containsKey(word)) {
				wordfreq.put(word, wordfreq.get(word) + 1);
			} else {
				wordfreq.put(word, 1);
			}
		}

		for (String word : goldwords) {
			if (goldwordfreq.containsKey(word)) {
				goldwordfreq.put(word, goldwordfreq.get(word) + 1);
			} else {
				goldwordfreq.put(word, 1);
			}
		}

		for (String word : goldwords) {
			if (words.contains(word)) {
				commonwords.add(word);
				cosinesum += goldwordfreq.get(word) * wordfreq.get(word);
			}
		}

		for (String word : goldwords) {
			sumgoldwords += goldwordfreq.get(word) * goldwordfreq.get(word);
		}

		for (String word : commonwords) {
			sumwords += wordfreq.get(word) * wordfreq.get(word);
		}

		sumwords = Math.sqrt(sumwords);
		sumgoldwords = Math.sqrt(sumgoldwords);

		if (sumgoldwords != 0 && sumwords != 0) {
			return cosinesum / (sumwords * sumgoldwords);
		}

		return 0;

	}

	public static String join(ArrayList<String> list, String delim) {
		StringBuilder st = new StringBuilder();

		for (String temp : list) {
			st.append(temp + delim);
		}

		return st.toString();
	}

	public static ArrayList<String> toArrayList(String[] ar) {
		ArrayList<String> temp = new ArrayList<String>();
		for (int i = 0; i < ar.length; i++) {
			temp.add(ar[i]);
		}
		return temp;
	}

	public static ArrayList<String> mergetoFirstArrayList(ArrayList<String> a,
			ArrayList<String> b) {
		for (String temp : b) {
			a.add(temp);
		}
		return a;
	}

	public static String categorizeurl(String url) throws IOException {
		String url_type = "undecided";
		Document html_content = Jsoup.connect(url).get();

		// check for blog providers name in the url

		/*
		 * ArrayList<String> blogproviderslist=readGolden("blog.txt");
		 * 
		 * if (checkforwordinurl(url,blogproviderslist)) return "blog";
		 * 
		 * 
		 * //check for 'wiki' word in the url: high precedence
		 * 
		 * if (url.contains("wiki")) return "wiki";
		 * 
		 * //check for 'forum', 'news' or 'blog' in the url: equal precedence
		 * int ct=0;
		 * 
		 * if(url.contains("forum")){ url_type="forum"; ct+=1; }
		 * if(url.contains("blog")){ url_type="blog"; ct+=1; }
		 * if(url.contains("news")){ url_type="news"; ct+=1; } if( ct>1){
		 * url_type="undecided"; } else if( ct==1){ return url_type; }
		 * 
		 * //check if it's a forum: by cosine similarity on the 'class'
		 * attribute of <tr>, <td> and <table> tags
		 */
		ArrayList<String> forumclassnamelist = readGolden("forum.txt");

		ArrayList<String> tags = new ArrayList<String>();
		tags.add("tr");
		tags.add("td");
		tags.add("table");

		ArrayList<String> classlist = extractallclassnames(tags, "class",
				html_content);
		ArrayList<String> cleanedclasslist = new ArrayList<String>();
		// System.out.println("HI");
		// System.out.println(classlist.toString());

		tags = new ArrayList<String>();
		tags.add("nav");
		tags.add("header");
		tags.add("footer");

		ArrayList<String> contentlist = extractallfromtag(tags, html_content);

		// System.out.println(contentlist.toString());

		// check if the classnames contain any of the words from the 'forum'
		// list
		for (String classname : classlist) {
			for (String forumword : forumclassnamelist) {
				if (classname.contains(forumword))
					cleanedclasslist.add(forumword);
			}
		}

		// System.out.println(cleanedclasslist.toString());

		double forumscore;
		forumscore = cosinesimilaritymeasure(cleanedclasslist,
				forumclassnamelist);
		// print('forum score::'+ str(forumscore))
		if (forumscore >= 0.4)
			return "forum";

		// check if a news website: check the nav, header and footer data (all
		// content, class and tags within), use similarity

		ArrayList<String> newslist = readGolden("news.txt");

		String contentlistJoined = join(contentlist, " ");
		contentlistJoined = contentlistJoined.replaceAll(
				"[^\\p{IsDigit}\\p{IsAlphabetic}]", " ");

		ArrayList<String> contentlistcleaned = toArrayList(contentlistJoined
				.split(" "));
		// System.out.println(contentlistcleaned.toString());
		double newsscore;
		newsscore = cosinesimilaritymeasure(contentlistcleaned, newslist);
		// print('news score::'+ str(newsscore))
		if (newsscore > 0.4)
			return "news";

		// check if a classified or shopping website

		ArrayList<String> shoppinglist = readGolden("shopping.txt");
		ArrayList<String> classifiedlist = readGolden("classified.txt");

		String html_content_text = html_content.text().replaceAll(
				"[^\\p{IsDigit}\\p{IsAlphabetic}]", " ");

		ArrayList<String> html_content_text_ngramed = mergetoFirstArrayList(
				nGrams(html_content_text, 1), nGrams(html_content_text, 2));

		// System.out.println(html_content_text_ngramed.toString());

		double classifiedscore;
		classifiedscore = cosinesimilaritymeasure(html_content_text_ngramed,
				classifiedlist);
		double shoppingscore;
		shoppingscore = cosinesimilaritymeasure(html_content_text_ngramed,
				shoppinglist);
		// print('classified score::'+ str(classifiedscore))
		// print('shopping score::'+ str(shoppingscore))
		if (classifiedscore > shoppingscore) {
			if (classifiedscore > 0.4)
				return "classified";
		}
		if (shoppingscore > classifiedscore) {
			if (shoppingscore > 0.4)
				return "shopping";
		}

		return url_type;

	}

	public static void main(String[] args) throws IOException {
		System.out.println(Categorizer.categorizeurl("http://www.cnn.com/"));
	}

}
