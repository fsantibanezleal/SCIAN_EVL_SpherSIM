close all
x0 = [0 2 4 6 8 10    0 2 4 6 8 10    0 2 4 6 8 10     0 2 4 6 8 10];
y0 = [3 3 3 3 3 3     6 6 6 6 6 6     9 9 9 9 9  9     0 0 0 0 0 0];

[vX,vY]=voronoi(x0,y0);
[vV,vC]=voronoin([x0(:) y0(:)]);

f1 = figure;
voronoi(x0,y0)

f2 = figure;
a1 = subplot(1,1,1);
for idxT = 1:1000
    x0 = x0 + 0.1.*(rand(size(x0))-0.5);
    y0 = y0 + 0.1.*(rand(size(y0))-0.5);
    
    x0(x0 > 10) = 10; 
    x0(x0 <  0) =  0;    
    y0(y0 > 10) = 10; 
    y0(y0 <  0) =  0;    
    
    [vX,vY]=voronoi(x0,y0);
    [vV,vC]=voronoin([x0(:) y0(:)]);

    hold off
    plot(a1,x0,y0,'c*')
    axis([1 8 1 8])
    hold on
    plot(a1,vX,vY)
    %nCells = size(vC,1);
    %for idxCell = 1:nCells
    %    vC{idxCell} = [vC{idxCell} vC{idxCell}(1)];
    %    plot(a1,vV(vC{idxCell}',1),vV(vC{idxCell}',2))
    %end
    axis([1 8 1 8])    
    title(['iteration ' num2str(idxT)]);
    pause(0.1)
end
