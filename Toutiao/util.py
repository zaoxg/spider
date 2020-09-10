import re
import hashlib


def _word_split_(word: str):
    result = []
    count = word.count('&')
    if count == 0:
        sub = word.replace("(", "").replace(")", "").replace("|", " ").split(' !')[0]
        # result = Arrays.asList(sub.split(" "));
        result.append(sub.split(' ')[0])
    elif count == 1:
        s1 = word[0: word.index("&")].replace("(", "").replace(")", "").replace("|", " ")
        s2 = word[word.rindex("&")].replace("&(", "").replace(")", "").replace("|", " ").replace("!", "-")
        list1 = s1.split(" ")
        list2 = s2.split(" ")
        for str1 in list1:
            for str2 in list2:
                result.append((str1 + '' + str2).split(' !')[0])
    else:
        s1 = word[0: word.index("&")].replace("(", "").replace(")", "").replace("|", " ")
        s2 = word[word.index("&"): word.rindex("&")].replace("&(", "").replace(")", "").replace("|", " ")
        s3 = word[word.rindex("&"):].replace("&(", "").replace(")", "").replace("|", " ").replace("!", "-")
        list1 = s1.split(" ")
        list2 = s2.split(" ")
        list3 = s3.split(" ")
        # print(list1, list2, list3)
        for str1 in list1:
            for str2 in list2:
                for str3 in list3:
                    result.append((str1 + ' ' + str2 + '' + str3).split(' !')[0])
    return result


def _word_split(word: str):
    result = []
    count = word.count('&')
    if count == 0:
        sub = word.replace("(", "").replace(")", "").replace("|", " ")
        # result = Arrays.asList(sub.split(" "));
        result.append(sub.split(' ')[0])
    elif count == 1:
        s1 = word[0: word.index("&")].replace("(", "").replace(")", "").replace("|", " ")
        s2 = word[word.rindex("&")].replace("&(", "").replace(")", "").replace("|", " ").replace("!", "-")
        list1 = s1.split(" ")
        list2 = s2.split(" ")
        for str1 in list1:
            for str2 in list2:
                result.append(str1 + '' + str2)
    else:
        s1 = word[0: word.index("&")].replace("(", "").replace(")", "").replace("|", " ")
        s2 = word[word.index("&"): word.rindex("&")].replace("&(", "").replace(")", "").replace("|", " ")
        s3 = word[word.rindex("&"):].replace("&(", "").replace(")", "").replace("|", " ").replace("!", "-")
        list1 = s1.split(" ")
        list2 = s2.split(" ")
        list3 = s3.split(" ")
        # print(list1, list2, list3)
        for str1 in list1:
            for str2 in list2:
                for str3 in list3:
                    result.append(str1 + ' ' + str2 + '' + str3)
    return result


def encrypt_md5(arg):
    md5 = hashlib.md5()
    md5.update(arg.encode(encoding='utf-8'))
    return md5.hexdigest()
