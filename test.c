int sum(int x, int y){
 int count =  0;
 for(int item =0 ;item<10;item++){
 count+=x;
}
count+=y;
return count;
}   

int main(){
   int a;
  scanf("%d",&a);
   int b;
  scanf("%d",&b);
  int sss= sum(a,b);
 printf("%d",sss);
 return 0;
 
}