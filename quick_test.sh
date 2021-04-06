for d in */ ; do
    cd $d
    cogment run generate
    cogment run build
    cogment run start &
    sleep 4
    cogment run stop
    sleep 4
    cd ..
done