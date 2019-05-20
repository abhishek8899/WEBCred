
document.body.style.background = "lightgray";

divs = document.getElementsByClassName('g');

urls = document.getElementsByClassName('iUh30');


var i,j;
var score=[];
var divtobesorted=[]
var urltobesorted=[]



for(i=0;i<urls.length;i++)
	// if(urls[i].className=="iUh30")
		urltobesorted.push(urls[i]);


for(i=0;i<divs.length;i++)
	if(divs[i].className=="g" && divs[i].id=="")
		divtobesorted.push(divs[i]);


for(i=0;i<urltobesorted.length;i++)
{
	// score from webcred python script
	// temporarily taken as random

	score.push(Math.random());
}

// console.log(urltobesorted);
// console.log(divtobesorted);


// sort div according to the score
// O(N*N) - No need for O(NlogN) - N~10

for(i=0;i<score.length;i++)	
	for(j=i+1;j<score.length;j++)
		if(score[i]<score[j])
		{
			tmp = score[i];
			score[i] = score[j];
			score[j] = tmp;

			tmp1 = divtobesorted[i].textContent;
			tmp2 = divtobesorted[i].innerHTML;
	
			divtobesorted[i].textContent = divtobesorted[j].textContent;
			divtobesorted[i].innerHTML = divtobesorted[j].innerHTML;
			divtobesorted[j].textContent = tmp1;
			divtobesorted[j].innerHTML = tmp2;
			// console.log(divtobesorted[i].textContent)
		}

// console.log(urltobesorted[0]);
// console.log("finished")

// document.getElementsByClassName('g') = divs;
// document.getElementsByTagName('cite') = urls;
