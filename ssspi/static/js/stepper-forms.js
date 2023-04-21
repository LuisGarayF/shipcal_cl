 
 /* Stepper Forms Config*/
 var stepper = document.querySelector('.stepper');
 var stepperInstace = new MStepper(stepper)
    
 function someFunction(destroyFeedback) {
     setTimeout(function () {
         destroyFeedback(true);
     }, 1000);
 }